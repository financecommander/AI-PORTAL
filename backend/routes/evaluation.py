"""
Evaluation API routes — Gap #3.

FastAPI endpoints for the evaluation framework:
- GET  /api/evaluation/suites       — list available benchmark suites
- GET  /api/evaluation/records      — list evaluation records
- GET  /api/evaluation/records/{id} — get specific evaluation
- POST /api/evaluation/run          — trigger a benchmark run
- POST /api/evaluation/compare      — compare models on a benchmark
- POST /api/evaluation/regression   — check for regressions
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.evaluation.recorder import EvaluationRecorder
from backend.evaluation.runner import BenchmarkRunner
from backend.evaluation.comparator import ModelComparator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

# Module-level singletons (initialized on first import or via init_evaluation())
_recorder: Optional[EvaluationRecorder] = None
_runner: Optional[BenchmarkRunner] = None
_comparator: Optional[ModelComparator] = None


def init_evaluation(storage_dir: Optional[Path] = None) -> None:
    """Initialize the evaluation subsystem. Call once at app startup."""
    global _recorder, _runner, _comparator
    storage_path = (storage_dir or Path("data")) / "evaluations.json"
    _recorder = EvaluationRecorder(storage_path)
    _runner = BenchmarkRunner(_recorder)
    _comparator = ModelComparator(_recorder)
    logger.info("Evaluation subsystem initialized (storage: %s)", storage_path)


def _get_recorder() -> EvaluationRecorder:
    if _recorder is None:
        init_evaluation()
    return _recorder  # type: ignore


def _get_runner() -> BenchmarkRunner:
    if _runner is None:
        init_evaluation()
    return _runner  # type: ignore


def _get_comparator() -> ModelComparator:
    if _comparator is None:
        init_evaluation()
    return _comparator  # type: ignore


# ── Request/Response Models ──────────────────────────────────


class RunBenchmarkRequest(BaseModel):
    benchmark: str
    model_name: str
    model_version: str
    run_by: Optional[str] = None
    seed: Optional[int] = None
    comparison_baseline: Optional[str] = None


class CompareRequest(BaseModel):
    benchmark: str
    model_specs: List[str]  # ["model_name/version", ...]


class RegressionCheckRequest(BaseModel):
    model_name: str
    current_version: str
    previous_version: str
    benchmark: str
    threshold: float = 0.05


# ── Endpoints ────────────────────────────────────────────


@router.get("/suites")
async def list_suites() -> List[Dict[str, Any]]:
    """List available benchmark suites."""
    return _get_runner().list_suites()


@router.get("/records")
async def list_records(
    model_name: Optional[str] = None,
    benchmark: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """List evaluation records with optional filters."""
    records = _get_recorder().list_records(
        model_name=model_name, benchmark=benchmark, limit=limit
    )
    return [r.to_dict() for r in records]


@router.get("/records/{evaluation_id}")
async def get_record(evaluation_id: str) -> Dict[str, Any]:
    """Get a specific evaluation record."""
    record = _get_recorder().get(evaluation_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Evaluation '{evaluation_id}' not found")
    return record.to_dict()


@router.post("/compare")
async def compare_models(req: CompareRequest) -> Dict[str, Any]:
    """Compare models on a specific benchmark."""
    result = _get_comparator().compare(req.benchmark, req.model_specs)
    return result.to_dict()


@router.post("/regression")
async def check_regression(req: RegressionCheckRequest) -> Dict[str, Any]:
    """Check for regressions between model versions."""
    return _get_comparator().regression_check(
        model_name=req.model_name,
        current_version=req.current_version,
        previous_version=req.previous_version,
        benchmark=req.benchmark,
        threshold=req.threshold,
    )
