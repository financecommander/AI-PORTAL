"""
Usage routes (stub implementation).
"""
from fastapi import APIRouter


router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/")
async def get_usage():
    """Get usage statistics (stub)."""
    return {"status": "stub", "message": "Usage route not yet implemented"}
