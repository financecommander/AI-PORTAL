"""
Model Registry API routes — Gap #4.

FastAPI endpoints for the model registry:
- GET    /api/models                        — list models
- POST   /api/models                        — register a model
- GET    /api/models/{name}/{version}       — get specific model
- GET    /api/models/{name}/versions        — list versions of a model
- GET    /api/models/{name}/latest          — get latest version
- POST   /api/models/{name}/{version}/promote   — promote lifecycle
- POST   /api/models/{name}/{version}/deprecate — deprecate model
- POST   /api/models/{name}/{version}/transition — arbitrary transition
- PATCH  /api/models/{name}/{version}/scores     — update eval scores
- DELETE /api/models/{name}/{version}       — delete (archived only)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.model_registry.registry import ModelRegistry, ModelRecord

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["model-registry"])

# Module-level singleton
_registry: Optional[ModelRegistry] = None


def init_model_registry(storage_dir: Optional[Path] = None) -> None:
    """Initialize the model registry. Call once at app startup."""
    global _registry
    storage_path = (storage_dir or Path("data")) / "model_registry.json"
    _registry = ModelRegistry(storage_path)
    logger.info("Model registry initialized (storage: %s)", storage_path)


def _get_registry() -> ModelRegistry:
    if _registry is None:
        init_model_registry()
    return _registry  # type: ignore


# ── Request Models ─────────────────────────────────────────


class RegisterModelRequest(BaseModel):
    model_name: str
    model_version: str
    model_type: str
    provider: Optional[str] = None
    architecture: Optional[str] = None
    parameter_count: Optional[int] = None
    quantization: Optional[str] = None
    compression_ratio: Optional[float] = None
    training_dataset: Optional[str] = None
    training_config: Dict[str, Any] = {}
    runtime_targets: List[str] = ["cpu"]
    cost_per_1m_input: Optional[float] = None
    cost_per_1m_output: Optional[float] = None
    max_context_tokens: Optional[int] = None
    artifact_ref: Optional[str] = None
    parent_model: Optional[str] = None
    registered_by: Optional[str] = None
    tags: Dict[str, str] = {}


class TransitionRequest(BaseModel):
    new_status: str


class UpdateScoresRequest(BaseModel):
    scores: Dict[str, float]


# ── Endpoints ────────────────────────────────────────────


@router.get("")
async def list_models(
    model_type: Optional[str] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """List registered models with optional filters."""
    models = _get_registry().list_models(
        model_type=model_type,
        provider=provider,
        status=status,
        limit=limit,
    )
    return [m.to_dict() for m in models]


@router.post("", status_code=201)
async def register_model(req: RegisterModelRequest) -> Dict[str, Any]:
    """Register a new model version."""
    try:
        record = _get_registry().register(
            model_name=req.model_name,
            model_version=req.model_version,
            model_type=req.model_type,
            provider=req.provider,
            architecture=req.architecture,
            parameter_count=req.parameter_count,
            quantization=req.quantization,
            compression_ratio=req.compression_ratio,
            training_dataset=req.training_dataset,
            training_config=req.training_config,
            runtime_targets=req.runtime_targets,
            cost_per_1m_input=req.cost_per_1m_input,
            cost_per_1m_output=req.cost_per_1m_output,
            max_context_tokens=req.max_context_tokens,
            artifact_ref=req.artifact_ref,
            parent_model=req.parent_model,
            registered_by=req.registered_by,
            tags=req.tags,
        )
        return record.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{model_name}/{model_version}")
async def get_model(model_name: str, model_version: str) -> Dict[str, Any]:
    """Get a specific model version."""
    record = _get_registry().get(model_name, model_version)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}/{model_version}' not found")
    return record.to_dict()


@router.get("/{model_name}/versions")
async def list_versions(model_name: str) -> List[Dict[str, Any]]:
    """List all versions of a model."""
    versions = _get_registry().list_versions(model_name)
    return [v.to_dict() for v in versions]


@router.get("/{model_name}/latest")
async def get_latest(model_name: str) -> Dict[str, Any]:
    """Get the latest version of a model."""
    record = _get_registry().get_latest(model_name)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No versions found for '{model_name}'")
    return record.to_dict()


@router.post("/{model_name}/{model_version}/promote")
async def promote_model(model_name: str, model_version: str) -> Dict[str, Any]:
    """Promote a model one step in the lifecycle."""
    try:
        record = _get_registry().promote(model_name, model_version)
        return record.to_dict()
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{model_name}/{model_version}/deprecate")
async def deprecate_model(model_name: str, model_version: str) -> Dict[str, Any]:
    """Deprecate a deployed model."""
    try:
        record = _get_registry().deprecate(model_name, model_version)
        return record.to_dict()
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{model_name}/{model_version}/transition")
async def transition_model(
    model_name: str,
    model_version: str,
    req: TransitionRequest,
) -> Dict[str, Any]:
    """Transition a model to a specific lifecycle status."""
    try:
        record = _get_registry().transition(model_name, model_version, req.new_status)
        return record.to_dict()
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{model_name}/{model_version}/scores")
async def update_scores(
    model_name: str,
    model_version: str,
    req: UpdateScoresRequest,
) -> Dict[str, Any]:
    """Attach or update evaluation scores for a model."""
    try:
        record = _get_registry().update_scores(model_name, model_version, req.scores)
        return record.to_dict()
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{model_name}/{model_version}")
async def delete_model(model_name: str, model_version: str) -> Dict[str, str]:
    """Delete a model (must be archived first)."""
    try:
        deleted = _get_registry().delete(model_name, model_version)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}/{model_version}' not found")
        return {"status": "deleted", "model": f"{model_name}/{model_version}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
