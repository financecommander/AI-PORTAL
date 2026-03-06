"""Blueprint session endpoints for AI Portal.

Manages Blueprint workflow sessions — CRUD, parse, generate, validate.
Execution is delegated to Swarm Mainframe (super-duper-spork).

These endpoints require JWT authentication via the portal auth middleware.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

# ── In-memory store (swap for PostgreSQL via database module in production) ──

_sessions: dict[str, dict] = {}


# ── Request / Response Models ────────────────────────────────────────────────

class BlueprintNodeModel(BaseModel):
    id: str
    type: str
    label: str
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})
    properties: dict[str, Any] = Field(default_factory=dict)
    children: list[str] = Field(default_factory=list)


class BlueprintEdgeModel(BaseModel):
    id: str
    source: str
    target: str
    label: str = ""
    edge_type: str = "default"


class BlueprintGraphModel(BaseModel):
    nodes: list[BlueprintNodeModel] = Field(default_factory=list)
    edges: list[BlueprintEdgeModel] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class CreateBlueprintRequest(BaseModel):
    name: str
    description: str = ""
    orc_source: str = ""
    graph: BlueprintGraphModel | None = None


class UpdateBlueprintRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    orc_source: str | None = None
    graph: BlueprintGraphModel | None = None


class ParseRequest(BaseModel):
    source: str


class GenerateRequest(BaseModel):
    nodes: list[BlueprintNodeModel] = Field(default_factory=list)
    edges: list[BlueprintEdgeModel] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class ValidateRequest(BaseModel):
    source: str


# ── Auth dependency (reuse portal JWT) ───────────────────────────────────────

def get_current_user() -> str:
    """Stub — wired to portal JWT middleware in production."""
    return "authenticated_user"


# ── Sessions CRUD ────────────────────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(user: str = Depends(get_current_user)):
    """List all Blueprint sessions for the authenticated user."""
    user_sessions = [s for s in _sessions.values() if s["created_by"] == user]
    user_sessions.sort(key=lambda s: s["updated_at"], reverse=True)
    return user_sessions


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, user: str = Depends(get_current_user)):
    """Get a specific Blueprint session."""
    session = _sessions.get(session_id)
    if not session or session["created_by"] != user:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/sessions", status_code=201)
async def create_session(req: CreateBlueprintRequest, user: str = Depends(get_current_user)):
    """Create a new Blueprint session."""
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    session = {
        "session_id": session_id,
        "name": req.name,
        "description": req.description,
        "status": "draft",
        "orc_source": req.orc_source,
        "graph": req.graph.model_dump() if req.graph else None,
        "created_by": user,
        "created_at": now,
        "updated_at": now,
        "execution_id": None,
        "validation_errors": [],
    }
    _sessions[session_id] = session
    logger.info("Blueprint session created: %s by %s", session_id, user)
    return session


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, req: UpdateBlueprintRequest, user: str = Depends(get_current_user)):
    """Update a Blueprint session (partial)."""
    session = _sessions.get(session_id)
    if not session or session["created_by"] != user:
        raise HTTPException(status_code=404, detail="Session not found")

    if req.name is not None:
        session["name"] = req.name
    if req.description is not None:
        session["description"] = req.description
    if req.orc_source is not None:
        session["orc_source"] = req.orc_source
    if req.graph is not None:
        session["graph"] = req.graph.model_dump()
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str, user: str = Depends(get_current_user)):
    """Delete a Blueprint session."""
    session = _sessions.get(session_id)
    if not session or session["created_by"] != user:
        raise HTTPException(status_code=404, detail="Session not found")
    del _sessions[session_id]
    logger.info("Blueprint session deleted: %s", session_id)


# ── Parse / Generate / Validate ──────────────────────────────────────────────

@router.post("/parse")
async def parse_orc(req: ParseRequest, user: str = Depends(get_current_user)):
    """Parse .orc source into a visual graph representation."""
    try:
        from orchestra.blueprint_editor.editor import BlueprintEditor
        editor = BlueprintEditor()
        graph = editor.orc_to_graph(req.source)
        if graph is None:
            return {"nodes": [], "edges": [], "metadata": {}}
        return graph.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {e}")


@router.post("/generate")
async def generate_orc(req: GenerateRequest, user: str = Depends(get_current_user)):
    """Generate .orc source from a visual graph."""
    try:
        from orchestra.blueprint_editor.editor import BlueprintEditor
        editor = BlueprintEditor()
        graph_data = {
            "nodes": [n.model_dump() for n in req.nodes],
            "edges": [e.model_dump() for e in req.edges],
            "metadata": req.metadata,
        }
        source = editor.graph_to_orc(graph_data)
        return {"source": source}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generate error: {e}")


@router.post("/validate")
async def validate_orc(req: ValidateRequest, user: str = Depends(get_current_user)):
    """Validate .orc source."""
    try:
        from orchestra.blueprint_editor.editor import BlueprintEditor
        editor = BlueprintEditor()
        result = editor.validate_orc(req.source)
        return {
            "valid": result.get("valid", False),
            "errors": result.get("errors", []),
            "warnings": result.get("warnings", []),
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
        }


# ── Triton Model Listing ────────────────────────────────────────────────────

@router.get("/models")
async def list_triton_models(user: str = Depends(get_current_user)):
    """List available Triton models from the registry."""
    try:
        from orchestra.triton_registry.registry import TritonModelRegistry
        registry = TritonModelRegistry()
        return registry.get_lsp_entries()
    except Exception as e:
        logger.warning("Failed to load Triton models: %s", e)
        return []
