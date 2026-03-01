"""Conversation history routes — CRUD for persistent chat threads."""

import re
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlmodel import Session, select, col, func

from backend.auth.authenticator import get_current_user
from backend.database import engine
from backend.models import Conversation, Message

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

router = APIRouter()


# ── Request/Response models ─────────────────────────────────────


class ConversationCreateRequest(BaseModel):
    provider: str = ""
    model: str = ""
    mode: str = "direct"  # direct, specialist
    specialist_id: Optional[str] = None


class MessageSaveRequest(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class ConversationUpdateRequest(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class ConversationResponse(BaseModel):
    uuid: str
    title: str
    provider: str
    model: str
    mode: str
    specialist_id: Optional[str]
    message_count: int = 0
    created_at: str
    updated_at: str
    preview: str = ""  # first user message truncated


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    created_at: str


# ── Helpers ──────────────────────────────────────────────────────


def _get_user_id(current_user: dict) -> int:
    """Extract user ID from JWT payload."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user token")
    return int(user_id)


def _validate_uuid(value: str) -> str:
    """Validate that a path parameter is a proper UUID4 string."""
    if not _UUID_RE.match(value):
        raise HTTPException(status_code=400, detail="Invalid conversation UUID format")
    return value


def _auto_title(content: str) -> str:
    """Generate a short title from the first user message."""
    content = content.strip()
    if len(content) <= 50:
        return content
    # Cut at word boundary
    truncated = content[:50]
    last_space = truncated.rfind(" ")
    if last_space > 20:
        truncated = truncated[:last_space]
    return truncated + "..."


# ── Routes ───────────────────────────────────────────────────────


@router.get("/")
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """List user's conversations, newest first."""
    user_id = _get_user_id(current_user)

    with Session(engine) as session:
        # Get conversations with message count
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(col(Conversation.updated_at).desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = session.exec(statement).all()

        result = []
        for conv in conversations:
            # Get message count
            count_stmt = (
                select(func.count(Message.id))
                .where(Message.conversation_id == conv.id)
            )
            msg_count = session.exec(count_stmt).one()

            # Get preview (first user message)
            preview_stmt = (
                select(Message.content)
                .where(Message.conversation_id == conv.id)
                .where(Message.role == "user")
                .order_by(Message.id)
                .limit(1)
            )
            preview_content = session.exec(preview_stmt).first()
            preview = (preview_content or "")[:100]

            result.append(ConversationResponse(
                uuid=conv.uuid,
                title=conv.title,
                provider=conv.provider,
                model=conv.model,
                mode=conv.mode,
                specialist_id=conv.specialist_id,
                message_count=msg_count,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                preview=preview,
            ))

        return {"conversations": result, "total": len(result)}


@router.post("/")
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new conversation."""
    user_id = _get_user_id(current_user)

    conv = Conversation(
        uuid=str(uuid_mod.uuid4()),
        user_id=user_id,
        provider=request.provider,
        model=request.model,
        mode=request.mode,
        specialist_id=request.specialist_id,
    )

    with Session(engine) as session:
        session.add(conv)
        session.commit()
        session.refresh(conv)

        return {
            "uuid": conv.uuid,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
        }


@router.get("/{conversation_uuid}")
async def get_conversation(
    conversation_uuid: str,
    current_user: dict = Depends(get_current_user),
):
    """Load a conversation with all messages."""
    _validate_uuid(conversation_uuid)
    user_id = _get_user_id(current_user)

    with Session(engine) as session:
        statement = (
            select(Conversation)
            .where(Conversation.uuid == conversation_uuid)
            .where(Conversation.user_id == user_id)
        )
        conv = session.exec(statement).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Load messages
        msg_stmt = (
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.id)
        )
        messages = session.exec(msg_stmt).all()

        return {
            "uuid": conv.uuid,
            "title": conv.title,
            "provider": conv.provider,
            "model": conv.model,
            "mode": conv.mode,
            "specialist_id": conv.specialist_id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "messages": [
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    model=m.model,
                    input_tokens=m.input_tokens,
                    output_tokens=m.output_tokens,
                    cost_usd=m.cost_usd,
                    created_at=m.created_at.isoformat(),
                )
                for m in messages
            ],
        }


@router.post("/{conversation_uuid}/messages")
async def save_message(
    conversation_uuid: str,
    request: MessageSaveRequest,
    current_user: dict = Depends(get_current_user),
):
    """Save a message to a conversation."""
    _validate_uuid(conversation_uuid)
    user_id = _get_user_id(current_user)

    with Session(engine) as session:
        statement = (
            select(Conversation)
            .where(Conversation.uuid == conversation_uuid)
            .where(Conversation.user_id == user_id)
        )
        conv = session.exec(statement).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        msg = Message(
            conversation_id=conv.id,
            role=request.role,
            content=request.content,
            model=request.model,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            cost_usd=request.cost_usd,
        )
        session.add(msg)

        # Auto-title on first user message
        if conv.title == "New conversation" and request.role == "user":
            conv.title = _auto_title(request.content)

        # Update timestamp
        conv.updated_at = datetime.now(timezone.utc)
        session.add(conv)
        session.commit()
        session.refresh(msg)

        return {
            "id": msg.id,
            "conversation_title": conv.title,
        }


@router.put("/{conversation_uuid}")
async def update_conversation(
    conversation_uuid: str,
    request: ConversationUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update conversation metadata (title, model, etc.)."""
    _validate_uuid(conversation_uuid)
    user_id = _get_user_id(current_user)

    with Session(engine) as session:
        statement = (
            select(Conversation)
            .where(Conversation.uuid == conversation_uuid)
            .where(Conversation.user_id == user_id)
        )
        conv = session.exec(statement).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if request.title is not None:
            conv.title = request.title
        if request.provider is not None:
            conv.provider = request.provider
        if request.model is not None:
            conv.model = request.model

        conv.updated_at = datetime.now(timezone.utc)
        session.add(conv)
        session.commit()

        return {"uuid": conv.uuid, "title": conv.title}


@router.delete("/{conversation_uuid}")
async def delete_conversation(
    conversation_uuid: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a conversation and all its messages."""
    _validate_uuid(conversation_uuid)
    user_id = _get_user_id(current_user)

    with Session(engine) as session:
        statement = (
            select(Conversation)
            .where(Conversation.uuid == conversation_uuid)
            .where(Conversation.user_id == user_id)
        )
        conv = session.exec(statement).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Delete messages first — flush before conversation delete to
        # guarantee correct ordering (DB may lack ON DELETE CASCADE).
        msg_stmt = select(Message).where(Message.conversation_id == conv.id)
        messages = session.exec(msg_stmt).all()
        for msg in messages:
            session.delete(msg)
        session.flush()  # force message DELETEs to DB before conv DELETE

        session.delete(conv)
        session.commit()

        return {"deleted": True}

