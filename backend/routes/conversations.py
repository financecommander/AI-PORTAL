"""Conversation history routes — persistent multi-turn chat sessions."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from backend.auth.authenticator import get_current_user
from backend.database import get_session
from backend.models import Conversation, ConversationMessage

router = APIRouter()


# ── Request / response schemas ─────────────────────────────────

class MessageOut(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ConversationOut(BaseModel):
    conversation_id: str
    title: str
    specialist_id: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = []


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=200)
    specialist_id: Optional[str] = Field(default=None, max_length=50)
    provider: Optional[str] = Field(default=None, max_length=50)
    model: Optional[str] = Field(default=None, max_length=100)


class MessageCreate(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=100000)


class BulkMessagesCreate(BaseModel):
    messages: list[MessageCreate] = Field(..., min_length=1, max_length=500)


# ── Helpers ────────────────────────────────────────────────────

def _get_user_hash(current_user: dict) -> str:
    return current_user.get("sub", "")


def _conv_to_out(conv: Conversation, messages: list[ConversationMessage]) -> ConversationOut:
    return ConversationOut(
        conversation_id=conv.conversation_id,
        title=conv.title,
        specialist_id=conv.specialist_id,
        provider=conv.provider,
        model=conv.model,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageOut(role=m.role, content=m.content, timestamp=m.timestamp) for m in messages],
    )


# ── Routes ─────────────────────────────────────────────────────

@router.get("/", response_model=list[ConversationOut])
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all conversations for the authenticated user (no messages included)."""
    user_hash = _get_user_hash(current_user)
    convs = session.exec(
        select(Conversation)
        .where(Conversation.user_hash == user_hash)
        .order_by(Conversation.updated_at.desc())  # type: ignore[arg-type]
    ).all()
    return [_conv_to_out(c, []) for c in convs]


@router.post("/", response_model=ConversationOut, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new conversation."""
    user_hash = _get_user_hash(current_user)
    conv = Conversation(
        user_hash=user_hash,
        title=body.title,
        specialist_id=body.specialist_id,
        provider=body.provider,
        model=body.model,
    )
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return _conv_to_out(conv, [])


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a conversation with all its messages."""
    user_hash = _get_user_hash(current_user)
    conv = session.exec(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_hash == user_hash,
        )
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = session.exec(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.timestamp)  # type: ignore[arg-type]
    ).all()
    return _conv_to_out(conv, list(messages))


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a conversation and all its messages."""
    user_hash = _get_user_hash(current_user)
    conv = session.exec(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_hash == user_hash,
        )
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Delete messages first
    msgs = session.exec(
        select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        )
    ).all()
    for msg in msgs:
        session.delete(msg)

    session.delete(conv)
    session.commit()


@router.post("/{conversation_id}/messages", response_model=ConversationOut, status_code=201)
async def add_messages(
    conversation_id: str,
    body: BulkMessagesCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Append one or more messages to an existing conversation."""
    user_hash = _get_user_hash(current_user)
    conv = session.exec(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id,
            Conversation.user_hash == user_hash,
        )
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    now = datetime.now(timezone.utc)
    for msg in body.messages:
        session.add(
            ConversationMessage(
                conversation_id=conversation_id,
                role=msg.role,
                content=msg.content,
                timestamp=now,
            )
        )

    # Update conversation title from first user message if still default
    if conv.title == "New Conversation":
        first_user = next((m for m in body.messages if m.role == "user"), None)
        if first_user:
            conv.title = first_user.content[:80] + ("…" if len(first_user.content) > 80 else "")

    conv.updated_at = now
    session.add(conv)
    session.commit()
    session.refresh(conv)

    messages = session.exec(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.timestamp)  # type: ignore[arg-type]
    ).all()
    return _conv_to_out(conv, list(messages))
