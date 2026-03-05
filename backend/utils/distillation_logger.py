"""Async fire-and-forget conversation logger for knowledge distillation."""

import logging
from backend.database import get_session_context
from backend.models import ConversationTurn

logger = logging.getLogger(__name__)


async def log_conversation_turn(**kwargs):
    """Log a conversation turn to the database without blocking the response.

    Intended to be called via asyncio.create_task() so failures
    are silently logged rather than propagated to the caller.
    """
    try:
        with get_session_context() as session:
            turn = ConversationTurn(**kwargs)
            session.add(turn)
            session.commit()
    except Exception as e:
        logger.error(f"Failed to log conversation turn: {e}")
