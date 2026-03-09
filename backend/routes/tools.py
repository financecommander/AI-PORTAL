"""
AI-PORTAL Tools Route — Generic Tool Execution API

Exposes swarm tools (algorithms, infra modules, calculus-tools clients)
as callable endpoints for LLM function calling integration.

Endpoints:
    GET  /api/v2/tools/list          — List all available tools
    GET  /api/v2/tools/list/{format} — List tools in OpenAI/Anthropic format
    POST /api/v2/tools/execute       — Execute a tool by name
    POST /api/v2/tools/batch         — Execute multiple tools
    GET  /api/v2/tools/stats         — Tool execution statistics
    GET  /api/v2/tools/search        — Search tools by query
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# ─── Lazy import swarm tool registry ─────────────────────────────────

_registry = None


def _get_registry():
    """Lazy-load the swarm tool registry."""
    global _registry
    if _registry is None:
        try:
            from swarm.tool_registry import ToolRegistry
            _registry = ToolRegistry()
            results = _registry.auto_discover_all()
            logger.info("Tool registry loaded: %s", results)
        except ImportError:
            logger.warning("swarm.tool_registry not available — using empty registry")
            # Fallback: create a minimal registry
            _registry = _MinimalRegistry()
    return _registry


class _MinimalRegistry:
    """Fallback when swarm is not installed."""

    def list_tools(self, **kwargs):
        return []

    def list_openai_tools(self, **kwargs):
        return []

    def list_anthropic_tools(self, **kwargs):
        return []

    def execute(self, name, args):
        return {"error": "Tool registry not available", "success": False}

    async def execute_async(self, name, args):
        return {"error": "Tool registry not available", "success": False}

    def get(self, name):
        return None

    @property
    def count(self):
        return 0

    @property
    def stats(self):
        return {"registered": 0}


# ─── Request/Response Models ─────────────────────────────────────────

class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    timeout: float = Field(default=30.0, description="Timeout in seconds")


class ToolBatchRequest(BaseModel):
    calls: List[ToolExecuteRequest] = Field(..., description="List of tool calls")
    parallel: bool = Field(default=True, description="Execute in parallel")


class ToolExecuteResponse(BaseModel):
    tool: str
    output: Any = None
    success: bool
    elapsed_ms: float = 0.0
    error: Optional[str] = None


# ─── Endpoints ───────────────────────────────────────────────────────

@router.get("/tools/list")
async def list_tools(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
):
    """List all available tools."""
    registry = _get_registry()
    kwargs = {}
    if search:
        kwargs["search"] = search
    if tags:
        kwargs["tags"] = tags.split(",")

    tools = registry.list_tools(**kwargs)
    return {
        "tools": [t.to_dict() if hasattr(t, "to_dict") else t for t in tools],
        "count": len(tools),
        "total_registered": registry.count,
    }


@router.get("/tools/list/openai")
async def list_tools_openai(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
):
    """List tools in OpenAI function calling format."""
    registry = _get_registry()
    kwargs = {}
    if tags:
        kwargs["tags"] = tags.split(",")
    return {"tools": registry.list_openai_tools(**kwargs)}


@router.get("/tools/list/anthropic")
async def list_tools_anthropic(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
):
    """List tools in Anthropic tool use format."""
    registry = _get_registry()
    kwargs = {}
    if tags:
        kwargs["tags"] = tags.split(",")
    return {"tools": registry.list_anthropic_tools(**kwargs)}


@router.post("/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest):
    """Execute a single tool by name."""
    registry = _get_registry()

    spec = registry.get(request.tool_name)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    result = await registry.execute_async(request.tool_name, request.arguments)
    return ToolExecuteResponse(
        tool=request.tool_name,
        output=result.get("output"),
        success=result.get("success", False),
        elapsed_ms=result.get("elapsed_ms", 0),
        error=result.get("error"),
    )


@router.post("/tools/batch")
async def execute_batch(request: ToolBatchRequest):
    """Execute multiple tools, optionally in parallel."""
    registry = _get_registry()
    results = []

    if request.parallel:
        import asyncio
        tasks = [
            registry.execute_async(call.tool_name, call.arguments)
            for call in request.calls
        ]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, r in enumerate(raw_results):
            if isinstance(r, Exception):
                results.append({
                    "tool": request.calls[i].tool_name,
                    "success": False,
                    "error": str(r),
                })
            else:
                results.append(r)
    else:
        for call in request.calls:
            result = await registry.execute_async(call.tool_name, call.arguments)
            results.append(result)

    return {
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.get("success")),
    }


@router.get("/tools/search")
async def search_tools(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search tools by keyword."""
    registry = _get_registry()
    tools = registry.list_tools(search=q)[:limit]
    return {
        "query": q,
        "tools": [t.to_dict() if hasattr(t, "to_dict") else t for t in tools],
        "count": len(tools),
    }


@router.get("/tools/stats")
async def tool_stats():
    """Get tool execution statistics."""
    registry = _get_registry()
    return registry.stats
