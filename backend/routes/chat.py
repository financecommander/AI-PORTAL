"""
Chat routes (stub implementation).
"""
from fastapi import APIRouter


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def send_message():
    """Send a chat message (stub)."""
    return {"status": "stub", "message": "Chat route not yet implemented"}
