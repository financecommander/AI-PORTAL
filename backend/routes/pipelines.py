"""
Pipeline routes (stub implementation).
"""
from fastapi import APIRouter


router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/")
async def list_pipelines():
    """List all pipelines (stub)."""
    return {"status": "stub", "message": "Pipelines route not yet implemented"}


@router.post("/")
async def run_pipeline():
    """Run a pipeline (stub)."""
    return {"status": "stub", "message": "Pipelines route not yet implemented"}
