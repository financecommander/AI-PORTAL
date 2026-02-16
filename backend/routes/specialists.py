"""
Specialist routes (stub implementation).
"""
from fastapi import APIRouter


router = APIRouter(prefix="/specialists", tags=["specialists"])


@router.get("/")
async def list_specialists():
    """List all specialists (stub)."""
    return {"status": "stub", "message": "Specialists route not yet implemented"}


@router.post("/")
async def create_specialist():
    """Create a new specialist (stub)."""
    return {"status": "stub", "message": "Specialists route not yet implemented"}
