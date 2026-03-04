"""Console Intelligence API routes.

Endpoints:
    GET  /console/hosts         — list configured SSH hosts
    POST /console/hosts/test    — test connectivity to a host
    POST /console/execute       — NL → SSH execution (SSE stream)
    POST /console/raw           — direct SSH command (SSE stream)
"""

from __future__ import annotations

import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.auth.authenticator import get_current_user
from backend.console.hosts import get_hosts, get_host, reload_hosts
from backend.console.interpreter import translate_command
from backend.console.ssh_service import execute_ssh_command, test_connection

router = APIRouter()


# ── Request / Response models ─────────────────────────────────


class ConsoleRequest(BaseModel):
    """Natural-language console command request."""
    message: str = Field(..., min_length=1, max_length=2000)
    provider: str = Field(default="anthropic", pattern=r"^(openai|anthropic|google|grok|groq|deepseek|mistral)$")
    model: Optional[str] = Field(default=None, max_length=100)


class RawCommandRequest(BaseModel):
    """Direct SSH command (bypasses LLM)."""
    host: str = Field(..., min_length=1, max_length=64)
    command: str = Field(..., min_length=1, max_length=5000)
    timeout: int = Field(default=30, ge=5, le=300)


class TestHostRequest(BaseModel):
    """Test connectivity to a host."""
    alias: str = Field(..., min_length=1, max_length=64)


# ── Default model per provider ────────────────────────────────

_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "google": "gemini-2.0-flash",
    "grok": "grok-3-mini",
    "groq": "llama-3.3-70b-versatile",
    "deepseek": "deepseek-chat",
    "mistral": "mistral-large-latest",
}


# ── Endpoints ─────────────────────────────────────────────────


@router.get("/hosts")
async def list_hosts(user: dict = Depends(get_current_user)):
    """Return all configured SSH hosts."""
    hosts = get_hosts()
    return {
        "hosts": [h.to_dict() for h in hosts],
        "count": len(hosts),
    }


@router.post("/hosts/test")
async def test_host(
    request: TestHostRequest,
    user: dict = Depends(get_current_user),
):
    """Test SSH connectivity to a specific host."""
    host = get_host(request.alias)
    if not host:
        raise HTTPException(status_code=404, detail=f"Host '{request.alias}' not found")
    result = await test_connection(host)
    return result


@router.post("/hosts/reload")
async def reload_hosts_endpoint(user: dict = Depends(get_current_user)):
    """Reload hosts from configuration file."""
    reload_hosts()
    hosts = get_hosts()
    return {"reloaded": True, "count": len(hosts)}


@router.post("/execute")
async def execute_nl_command(
    request: ConsoleRequest,
    user: dict = Depends(get_current_user),
):
    """Translate natural language → SSH command and execute.

    Returns an SSE stream with events:
      - plan:   the interpreted command plan
      - stdout: live stdout output
      - stderr: live stderr output
      - status: exit code / completion status
      - error:  if something went wrong
    """
    model = request.model or _DEFAULT_MODELS.get(request.provider, "claude-sonnet-4-20250514")

    async def event_stream():
        # Phase 1: LLM interprets the command
        try:
            plan = await translate_command(
                user_input=request.message,
                provider_name=request.provider,
                model=model,
            )
        except Exception as exc:
            yield _sse("error", {"message": f"LLM translation failed: {exc}"})
            return

        # Send the plan to the frontend
        yield _sse("plan", {
            "host": plan.host,
            "command": plan.command,
            "explanation": plan.explanation,
            "risk": plan.risk,
            "error": plan.error,
        })

        if not plan.is_valid:
            yield _sse("error", {"message": plan.error or "Could not interpret command"})
            return

        # Resolve host
        host = get_host(plan.host)
        if not host:
            yield _sse("error", {"message": f"Host '{plan.host}' not found in configuration"})
            return

        # Phase 2: Execute via SSH
        yield _sse("executing", {"host": plan.host, "command": plan.command})

        async for chunk in execute_ssh_command(host, plan.command, timeout=30):
            yield _sse(chunk.stream, {"text": chunk.text})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/raw")
async def execute_raw_command(
    request: RawCommandRequest,
    user: dict = Depends(get_current_user),
):
    """Execute a raw SSH command (no LLM translation).

    Returns an SSE stream with stdout/stderr/status events.
    """
    host = get_host(request.host)
    if not host:
        raise HTTPException(status_code=404, detail=f"Host '{request.host}' not found")

    async def event_stream():
        yield _sse("executing", {"host": request.host, "command": request.command})
        async for chunk in execute_ssh_command(host, request.command, timeout=request.timeout):
            yield _sse(chunk.stream, {"text": chunk.text})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Helpers ────────────────────────────────────────────────────


def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"
