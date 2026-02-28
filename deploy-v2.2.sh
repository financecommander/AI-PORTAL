#!/bin/bash
set -e
echo "🚀 AI Portal v2.2 — Direct file deployment"
echo "============================================"
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌ Cannot find AI-PORTAL directory"; exit 1; }
echo "📁 Working in: $(pwd)"
echo ""
mkdir -p 'backend/auth'
cat > 'backend/auth/oauth.py' << 'FILEEOF_backend_auth_oauth_py'
"""OAuth authentication handlers for Google, Apple, and X (Twitter).

Lightweight implementation using direct HTTP calls to OAuth providers.
No heavy dependencies — just httpx for async HTTP.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timezone

import httpx
from sqlmodel import Session, select

from backend.database import engine
from backend.models import User
from backend.auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)


# ── Provider configs from env ───────────────────────────────────

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")

APPLE_CLIENT_ID = os.getenv("APPLE_OAUTH_CLIENT_ID", "")
APPLE_CLIENT_SECRET = os.getenv("APPLE_OAUTH_CLIENT_SECRET", "")

X_CLIENT_ID = os.getenv("X_OAUTH_CLIENT_ID", "")
X_CLIENT_SECRET = os.getenv("X_OAUTH_CLIENT_SECRET", "")


def _get_redirect_uri(provider: str) -> str:
    """Build redirect URI from environment."""
    base = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:3000")
    return f"{base}/auth/{provider}/callback"


# ── User upsert ─────────────────────────────────────────────────


def get_or_create_user(
    email: str,
    name: str = "",
    avatar_url: str = "",
    oauth_provider: str = "email",
    oauth_id: str = "",
) -> User:
    """Find existing user by email or create a new one."""
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if user:
            user.last_login = datetime.now(timezone.utc)
            if name and not user.name:
                user.name = name
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

        user = User(
            email=email,
            name=name,
            avatar_url=avatar_url,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_user_token(user: User) -> str:
    """Create JWT for an authenticated user."""
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "provider": user.oauth_provider,
    })


# ── Google OAuth ────────────────────────────────────────────────


async def google_get_auth_url() -> str:
    """Get Google OAuth authorization URL."""
    redirect_uri = _get_redirect_uri("google")
    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "access_type=offline&"
        "prompt=consent"
    )


async def google_exchange_code(code: str) -> Optional[User]:
    """Exchange Google auth code for user info, create/update user."""
    redirect_uri = _get_redirect_uri("google")

    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error(f"Google token exchange failed: {token_resp.text}")
            return None

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            logger.error(f"Google userinfo failed: {user_resp.text}")
            return None

        info = user_resp.json()
        return get_or_create_user(
            email=info["email"],
            name=info.get("name", ""),
            avatar_url=info.get("picture", ""),
            oauth_provider="google",
            oauth_id=info.get("id", ""),
        )


# ── Apple OAuth ─────────────────────────────────────────────────


async def apple_get_auth_url() -> str:
    """Get Apple Sign In authorization URL."""
    redirect_uri = _get_redirect_uri("apple")
    return (
        "https://appleid.apple.com/auth/authorize?"
        f"client_id={APPLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=name+email&"
        "response_mode=form_post"
    )


async def apple_exchange_code(code: str) -> Optional[User]:
    """Exchange Apple auth code for user info."""
    redirect_uri = _get_redirect_uri("apple")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://appleid.apple.com/auth/token",
            data={
                "code": code,
                "client_id": APPLE_CLIENT_ID,
                "client_secret": APPLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            logger.error(f"Apple token exchange failed: {token_resp.text}")
            return None

        tokens = token_resp.json()
        # Apple returns id_token as JWT — decode to get email
        import json
        import base64

        id_token = tokens.get("id_token", "")
        # Decode JWT payload (middle segment) without verification
        # (we already verified via Apple's token endpoint)
        payload_b64 = id_token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)  # pad
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        email = payload.get("email", "")
        if not email:
            logger.error("Apple auth: no email in id_token")
            return None

        return get_or_create_user(
            email=email,
            name="",  # Apple only sends name on first auth
            oauth_provider="apple",
            oauth_id=payload.get("sub", ""),
        )


# ── X (Twitter) OAuth 2.0 PKCE ─────────────────────────────────


async def x_get_auth_url(state: str = "random") -> str:
    """Get X OAuth 2.0 authorization URL."""
    redirect_uri = _get_redirect_uri("x")
    return (
        "https://twitter.com/i/oauth2/authorize?"
        f"response_type=code&"
        f"client_id={X_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=tweet.read+users.read+offline.access&"
        f"state={state}&"
        "code_challenge=challenge&"
        "code_challenge_method=plain"
    )


async def x_exchange_code(code: str) -> Optional[User]:
    """Exchange X auth code for user info."""
    redirect_uri = _get_redirect_uri("x")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "code": code,
                "client_id": X_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": "challenge",
            },
            auth=(X_CLIENT_ID, X_CLIENT_SECRET),
        )
        if token_resp.status_code != 200:
            logger.error(f"X token exchange failed: {token_resp.text}")
            return None

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # Get user info
        user_resp = await client.get(
            "https://api.twitter.com/2/users/me?user.fields=profile_image_url",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            logger.error(f"X userinfo failed: {user_resp.text}")
            return None

        data = user_resp.json().get("data", {})
        # X doesn't expose email easily — use username@x.com as placeholder
        username = data.get("username", "unknown")

        return get_or_create_user(
            email=f"{username}@x.com",
            name=data.get("name", username),
            avatar_url=data.get("profile_image_url", ""),
            oauth_provider="x",
            oauth_id=data.get("id", ""),
        )

FILEEOF_backend_auth_oauth_py
echo '  ✅ backend/auth/oauth.py'

mkdir -p 'backend'
cat > 'backend/main.py' << 'FILEEOF_backend_main_py'
"""FastAPI backend application for AI Portal v2.0."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.database import init_db
from backend.routes import pipelines
from backend.routes import auth as auth_routes
from backend.routes import chat as chat_routes
from backend.routes import specialists as specialist_routes
from backend.routes import usage as usage_routes
from backend.routes import direct_chat as direct_chat_routes
from backend.routes import conversations as conversation_routes
from backend.config.settings import settings
from backend.errors.exceptions import PortalError
from backend.middleware.rate_limiter import RateLimiterMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="FinanceCommander AI Portal",
    description="Multi-agent intelligence platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handler
@app.exception_handler(PortalError)
async def portal_error_handler(request: Request, exc: PortalError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

# Routes
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
app.include_router(specialist_routes.router, prefix="/specialists", tags=["specialists"])
app.include_router(usage_routes.router, prefix="/usage", tags=["usage"])
app.include_router(pipelines.router, prefix="/api/v2", tags=["pipelines"])
app.include_router(direct_chat_routes.router, prefix="/chat/direct", tags=["direct-chat"])
app.include_router(conversation_routes.router, prefix="/conversations", tags=["conversations"])


@app.get("/")
async def root():
    return {"message": "FinanceCommander AI Portal v2.0", "docs": "/docs", "status": "operational"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

FILEEOF_backend_main_py
echo '  ✅ backend/main.py'

mkdir -p 'backend/models'
cat > 'backend/models/__init__.py' << 'FILEEOF_backend_models___init___py'
"""Database models for backend v2.2."""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class UsageLog(SQLModel, table=True):
    """Usage log for individual requests."""

    __tablename__ = "usage_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_hash: str = Field(index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    specialist_id: Optional[str] = None


class PipelineRun(SQLModel, table=True):
    """High-level pipeline execution log."""

    __tablename__ = "pipeline_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    pipeline_id: str = Field(index=True, unique=True)
    pipeline_name: str
    user_hash: str = Field(index=True)
    query: str
    output: str
    total_tokens: int
    total_cost: float
    duration_ms: float
    status: str  # running, completed, failed
    error: Optional[str] = None
    agent_breakdown: str  # JSON string
    extra_metadata: str = Field(default="{}")  # JSON string - renamed from metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


# ── v2.2: User accounts + conversation history ──────────────────


class User(SQLModel, table=True):
    """User accounts with OAuth or email login."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = Field(default="")
    avatar_url: str = Field(default="")
    oauth_provider: str = Field(default="email")  # email, google, apple, x
    oauth_id: str = Field(default="")  # provider-specific user ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(SQLModel, table=True):
    """Persistent chat conversations."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)  # public-facing ID
    user_id: int = Field(index=True, foreign_key="users.id")
    title: str = Field(default="New conversation")
    provider: str = Field(default="")
    model: str = Field(default="")
    mode: str = Field(default="direct")  # direct, specialist
    specialist_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(SQLModel, table=True):
    """Individual messages within a conversation."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(index=True, foreign_key="conversations.id")
    role: str  # user, assistant
    content: str
    model: str = Field(default="")
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

FILEEOF_backend_models___init___py
echo '  ✅ backend/models/__init__.py'

mkdir -p 'backend/routes'
cat > 'backend/routes/auth.py' << 'FILEEOF_backend_routes_auth_py'
"""Authentication routes — email + OAuth (Google, Apple, X)."""

import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from backend.auth.authenticator import get_current_user
from backend.auth.oauth import (
    google_get_auth_url, google_exchange_code,
    apple_get_auth_url, apple_exchange_code,
    x_get_auth_url, x_exchange_code,
    get_or_create_user, create_user_token,
)

router = APIRouter()
ALLOWED_DOMAINS = {"gradeesolutions.com", "calculusresearch.io"}

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class LoginRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        v = v.lower().strip()
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email format")
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthCallbackRequest(BaseModel):
    code: str


# ── Email login (domain-restricted) ────────────────────────────


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email
    domain = email.split("@")[1]
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=401, detail="Email domain is not authorized")
    user = get_or_create_user(email=email, oauth_provider="email")
    token = create_user_token(user)
    return LoginResponse(access_token=token)


# ── User profile ────────────────────────────────────────────────


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Return current user profile from JWT."""
    return {
        "id": current_user.get("sub"),
        "email": current_user.get("email", ""),
        "name": current_user.get("name", ""),
        "avatar_url": current_user.get("avatar_url", ""),
        "provider": current_user.get("provider", "email"),
    }


# ── Google OAuth ────────────────────────────────────────────────


@router.get("/google")
async def google_auth():
    url = await google_get_auth_url()
    return {"auth_url": url}


@router.post("/google/callback", response_model=LoginResponse)
async def google_callback(request: OAuthCallbackRequest):
    user = await google_exchange_code(request.code)
    if not user:
        raise HTTPException(status_code=401, detail="Google authentication failed")
    return LoginResponse(access_token=create_user_token(user))


# ── Apple OAuth ─────────────────────────────────────────────────


@router.get("/apple")
async def apple_auth():
    url = await apple_get_auth_url()
    return {"auth_url": url}


@router.post("/apple/callback", response_model=LoginResponse)
async def apple_callback(request: OAuthCallbackRequest):
    user = await apple_exchange_code(request.code)
    if not user:
        raise HTTPException(status_code=401, detail="Apple authentication failed")
    return LoginResponse(access_token=create_user_token(user))


# ── X (Twitter) OAuth ───────────────────────────────────────────


@router.get("/x")
async def x_auth():
    url = await x_get_auth_url()
    return {"auth_url": url}


@router.post("/x/callback", response_model=LoginResponse)
async def x_callback(request: OAuthCallbackRequest):
    user = await x_exchange_code(request.code)
    if not user:
        raise HTTPException(status_code=401, detail="X authentication failed")
    return LoginResponse(access_token=create_user_token(user))

FILEEOF_backend_routes_auth_py
echo '  ✅ backend/routes/auth.py'

mkdir -p 'backend/routes'
cat > 'backend/routes/conversations.py' << 'FILEEOF_backend_routes_conversations_py'
"""Conversation history routes — CRUD for persistent chat threads."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select, col, func

from backend.auth.authenticator import get_current_user
from backend.database import engine
from backend.models import Conversation, Message

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
        uuid=str(uuid.uuid4()),
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

        # Delete messages first
        msg_stmt = select(Message).where(Message.conversation_id == conv.id)
        messages = session.exec(msg_stmt).all()
        for msg in messages:
            session.delete(msg)

        session.delete(conv)
        session.commit()

        return {"deleted": True}

FILEEOF_backend_routes_conversations_py
echo '  ✅ backend/routes/conversations.py'

mkdir -p '.'
cat > 'docker-compose.v2.yml' << 'FILEEOF_docker-compose_v2_yml'
services:
  db:
    image: postgres:16-alpine
    container_name: fc-portal-db
    environment:
      POSTGRES_DB: ai_portal
      POSTGRES_USER: ${DB_USER:-portal}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD required}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-portal} -d ai_portal"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: fc-portal-backend
    environment:
      DATABASE_URL: postgresql://${DB_USER:-portal}:${DB_PASSWORD}@db:5432/ai_portal
      JWT_SECRET: ${JWT_SECRET:?JWT_SECRET required}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:-${JWT_SECRET}}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      XAI_API_KEY: ${XAI_API_KEY:-}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}
      MISTRAL_API_KEY: ${MISTRAL_API_KEY:-}
      GROQ_API_KEY: ${GROQ_API_KEY:-}
      COURTLISTENER_API_KEY: ${COURTLISTENER_API_KEY:-}
      GOOGLE_OAUTH_CLIENT_ID: ${GOOGLE_OAUTH_CLIENT_ID:-}
      GOOGLE_OAUTH_CLIENT_SECRET: ${GOOGLE_OAUTH_CLIENT_SECRET:-}
      APPLE_OAUTH_CLIENT_ID: ${APPLE_OAUTH_CLIENT_ID:-}
      APPLE_OAUTH_CLIENT_SECRET: ${APPLE_OAUTH_CLIENT_SECRET:-}
      X_OAUTH_CLIENT_ID: ${X_OAUTH_CLIENT_ID:-}
      X_OAUTH_CLIENT_SECRET: ${X_OAUTH_CLIENT_SECRET:-}
      OAUTH_REDIRECT_BASE: ${OAUTH_REDIRECT_BASE:-http://localhost:3000}
      TRITON_CHECKPOINT_DIR: /app/triton/checkpoints
      TRITON_PATH: /app/triton
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    container_name: fc-portal-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
    driver: local

FILEEOF_docker-compose_v2_yml
echo '  ✅ docker-compose.v2.yml'

mkdir -p 'frontend/src/components'
cat > 'frontend/src/components/ConversationList.tsx' << 'FILEEOF_frontend_src_components_ConversationList_tsx'
import { useState, useEffect } from 'react';
import { Plus, Trash2, MessageSquare } from 'lucide-react';
import { api } from '../api/client';

interface ConversationItem {
  uuid: string;
  title: string;
  provider: string;
  model: string;
  mode: string;
  message_count: number;
  updated_at: string;
  preview: string;
}

interface ConversationListProps {
  activeId: string | null;
  onSelect: (uuid: string) => void;
  onNew: () => void;
}

export default function ConversationList({ activeId, onSelect, onNew }: ConversationListProps) {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadConversations = async () => {
    try {
      const data = await api.request<{ conversations: ConversationItem[] }>('/conversations/');
      setConversations(data.conversations);
    } catch {
      // silently fail — user might not be authed yet
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  // Refresh when activeId changes (new messages may have updated title)
  useEffect(() => {
    if (activeId) loadConversations();
  }, [activeId]);

  const handleDelete = async (e: React.MouseEvent, uuid: string) => {
    e.stopPropagation();
    try {
      await api.delete(`/conversations/${uuid}`);
      setConversations((prev) => prev.filter((c) => c.uuid !== uuid));
      if (activeId === uuid) onNew();
    } catch {
      // ignore
    }
  };

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffHours = diffMs / (1000 * 60 * 60);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${Math.floor(diffHours)}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div style={{ padding: '12px', color: 'var(--cr-text-dim)', fontSize: '12px' }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* New chat button */}
      <button
        onClick={onNew}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          margin: '8px 10px',
          padding: '8px 12px',
          borderRadius: 'var(--cr-radius-sm)',
          border: '1px solid var(--cr-border)',
          background: 'transparent',
          color: 'var(--cr-text-muted)',
          fontSize: '13px',
          cursor: 'pointer',
          transition: 'all 150ms',
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text)';
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)';
        }}
      >
        <Plus style={{ width: 14, height: 14 }} />
        New chat
      </button>

      {/* Conversation list */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 6px',
        }}
      >
        {conversations.length === 0 && (
          <div
            style={{
              padding: '20px 12px',
              textAlign: 'center',
              color: 'var(--cr-text-dim)',
              fontSize: '12px',
            }}
          >
            <MessageSquare
              style={{ width: 20, height: 20, margin: '0 auto 8px', opacity: 0.4 }}
            />
            No conversations yet
          </div>
        )}

        {conversations.map((conv) => {
          const isActive = conv.uuid === activeId;
          return (
            <button
              key={conv.uuid}
              onClick={() => onSelect(conv.uuid)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                width: '100%',
                padding: '10px 10px',
                margin: '1px 0',
                borderRadius: 'var(--cr-radius-xs)',
                border: 'none',
                background: isActive ? 'var(--cr-charcoal-deep)' : 'transparent',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'background 100ms',
                position: 'relative',
              }}
              onMouseEnter={(e) => {
                if (!isActive)
                  (e.currentTarget as HTMLButtonElement).style.background =
                    'rgba(42, 46, 50, 0.5)';
              }}
              onMouseLeave={(e) => {
                if (!isActive)
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              }}
            >
              <div style={{ flex: 1, overflow: 'hidden', minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: isActive ? 500 : 400,
                    color: isActive ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {conv.title}
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    color: 'var(--cr-text-dim)',
                    marginTop: '2px',
                  }}
                >
                  {formatTime(conv.updated_at)}
                  {conv.model && (
                    <span style={{ marginLeft: '6px', opacity: 0.7 }}>
                      {conv.model.split('/').pop()?.split('-').slice(0, 2).join('-')}
                    </span>
                  )}
                </div>
              </div>
              {/* Delete button — shows on hover via CSS would be ideal, but inline works */}
              <button
                onClick={(e) => handleDelete(e, conv.uuid)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: '2px',
                  cursor: 'pointer',
                  color: 'var(--cr-text-dim)',
                  opacity: 0.4,
                  transition: 'opacity 150ms, color 150ms',
                  flexShrink: 0,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.color = 'var(--cr-danger)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.4';
                  e.currentTarget.style.color = 'var(--cr-text-dim)';
                }}
                title="Delete conversation"
              >
                <Trash2 style={{ width: 13, height: 13 }} />
              </button>
            </button>
          );
        })}
      </div>
    </div>
  );
}

FILEEOF_frontend_src_components_ConversationList_tsx
echo '  ✅ frontend/src/components/ConversationList.tsx'

mkdir -p 'frontend/src/components'
cat > 'frontend/src/components/Sidebar.tsx' << 'FILEEOF_frontend_src_components_Sidebar_tsx'
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Sparkles,
  MessageSquare,
  Brain,
  BarChart3,
  Settings,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import clsx from 'clsx';
import ConversationList from './ConversationList';

const navItems = [
  { to: '/', icon: Sparkles, label: 'Chat' },
  { to: '/specialists', icon: MessageSquare, label: 'Specialists' },
  { to: '/pipelines', icon: Brain, label: 'Intelligence Pipelines' },
  { to: '/usage', icon: BarChart3, label: 'Usage & Costs' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

interface SidebarProps {
  onNavigate?: () => void;
  activeConversationId?: string | null;
  onSelectConversation?: (uuid: string) => void;
  onNewConversation?: () => void;
}

export default function Sidebar({
  onNavigate,
  activeConversationId = null,
  onSelectConversation,
  onNewConversation,
}: SidebarProps) {
  const { logout, user } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => {
    logout();
    navigate('/login');
    onNavigate?.();
  };

  return (
    <aside
      className="h-screen flex flex-col"
      style={{
        width: 'var(--sidebar-width)',
        background: 'var(--cr-charcoal)',
        borderRight: '1px solid var(--cr-border)',
      }}
    >
      {/* Brand */}
      <div className="px-5 py-5" style={{ borderBottom: '1px solid var(--cr-border)' }}>
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: '16px',
            fontWeight: 700,
            color: 'var(--cr-green-400)',
            letterSpacing: '0.04em',
            margin: 0,
          }}
        >
          CALCULUS LABS
        </h1>
        <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '2px' }}>
          AI Portal v2.2
        </p>
      </div>

      {/* Nav */}
      <nav className="py-3 px-3 space-y-1" style={{ borderBottom: '1px solid var(--cr-border)' }}>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={() => onNavigate?.()}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2 text-sm transition-all group',
                isActive ? 'font-medium' : '',
              )
            }
            style={({ isActive }) => ({
              borderRadius: 'var(--cr-radius-sm)',
              background: isActive ? 'var(--cr-charcoal-deep)' : 'transparent',
              color: isActive ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
              borderLeft: isActive
                ? '2px solid var(--cr-green-600)'
                : '2px solid transparent',
            })}
          >
            <Icon className="w-[18px] h-[18px] shrink-0" />
            <span className="flex-1">{label}</span>
            <ChevronRight
              className="w-4 h-4 opacity-0 group-hover:opacity-40 transition-opacity"
              style={{ color: 'var(--cr-text-dim)' }}
            />
          </NavLink>
        ))}
      </nav>

      {/* Conversation History */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <div
          style={{
            padding: '10px 14px 4px',
            fontSize: '10px',
            fontWeight: 600,
            color: 'var(--cr-text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
          }}
        >
          Recent chats
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <ConversationList
            activeId={activeConversationId}
            onSelect={(uuid) => {
              onSelectConversation?.(uuid);
              navigate('/');
              onNavigate?.();
            }}
            onNew={() => {
              onNewConversation?.();
              navigate('/');
              onNavigate?.();
            }}
          />
        </div>
      </div>

      {/* User + Sign Out */}
      <div className="px-3 py-3" style={{ borderTop: '1px solid var(--cr-border)' }}>
        {user && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '4px 8px',
              marginBottom: '6px',
            }}
          >
            {user.avatar_url ? (
              <img
                src={user.avatar_url}
                alt=""
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  border: '1px solid var(--cr-border)',
                }}
              />
            ) : (
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'var(--cr-green-900)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--cr-green-400)',
                }}
              >
                {(user.name || user.email).charAt(0).toUpperCase()}
              </div>
            )}
            <span
              style={{
                fontSize: '12px',
                color: 'var(--cr-text-muted)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {user.name || user.email}
            </span>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 text-sm w-full transition-all"
          style={{
            color: 'var(--cr-text-dim)',
            borderRadius: 'var(--cr-radius-sm)',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-danger)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-dim)';
          }}
        >
          <LogOut className="w-[18px] h-[18px]" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

FILEEOF_frontend_src_components_Sidebar_tsx
echo '  ✅ frontend/src/components/Sidebar.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/MessageBubble.tsx' << 'FILEEOF_frontend_src_components_chat_MessageBubble_tsx'
import { useState } from 'react';
import { FileText } from 'lucide-react';
import type { ChatMessage } from '../../types';
import { isImageType, formatFileSize } from '../../utils/fileUpload';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

type Segment = { type: 'text'; html: string } | { type: 'code'; content: string };

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function parseSegments(text: string): Segment[] {
  const segments: Segment[] = [];
  const parts = text.split(/(```[\w]*\n?[\s\S]*?```)/g);
  for (const part of parts) {
    const codeMatch = part.match(/^```[\w]*\n?([\s\S]*?)```$/);
    if (codeMatch) {
      segments.push({ type: 'code', content: codeMatch[1] });
    } else {
      segments.push({ type: 'text', html: renderInlineMarkdown(part) });
    }
  }
  return segments;
}

function renderInlineMarkdown(text: string): string {
  let html = escapeHtml(text);

  // Inline code (already HTML-escaped, so no XSS risk)
  html = html.replace(
    /`([^`]+)`/g,
    '<code style="background:var(--cr-charcoal-deep);padding:2px 6px;border-radius:4px;font-family:monospace">$1</code>',
  );

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Bullet lists
  html = html.replace(
    /^[ \t]*[-*] (.+)$/gm,
    '<li style="margin-left:16px;list-style:disc">$1</li>',
  );
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/g, '<ul style="margin:4px 0;padding:0">$&</ul>');

  // Numbered lists
  html = html.replace(
    /^[ \t]*\d+\. (.+)$/gm,
    '<li style="margin-left:16px;list-style:decimal">$1</li>',
  );

  // Newlines → <br>
  html = html.replace(/\n/g, '<br>');

  return html;
}

function CodeBlock({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <div style={{ position: 'relative', margin: '8px 0' }}>
      <pre
        style={{
          background: 'var(--cr-charcoal-deep)',
          fontFamily: 'monospace',
          fontSize: 14,
          padding: 12,
          borderRadius: 8,
          overflowX: 'auto',
          margin: 0,
          whiteSpace: 'pre',
        }}
      >
        {content}
      </pre>
      <button
        onClick={handleCopy}
        style={{
          position: 'absolute',
          top: 6,
          right: 8,
          background: 'var(--cr-border)',
          border: 'none',
          color: 'var(--cr-text-muted)',
          fontSize: 11,
          padding: '2px 8px',
          borderRadius: 4,
          cursor: 'pointer',
        }}
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
    </div>
  );
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const hasStats =
    !isStreaming &&
    message.tokens !== undefined &&
    message.cost_usd !== undefined;

  const segments = isUser ? null : parseSegments(message.content);

  return (
    <div
      className="animate-fade-in-up flex flex-col mb-4"
      style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}
    >
      <div
        style={{
          maxWidth: '80%',
          background: isUser ? 'var(--cr-green-900)' : 'var(--cr-charcoal)',
          color: isUser ? 'var(--cr-text)' : 'var(--cr-text)',
          borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
          padding: '10px 14px',
          wordBreak: 'break-word',
        }}
      >
        {isUser ? (
          <>
            {/* Render file attachments above message text */}
            {message.attachments && message.attachments.length > 0 && (
              <div
                style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: 6,
                  marginBottom: message.content.trim() ? 8 : 0,
                }}
              >
                {message.attachments.map((att, i) =>
                  isImageType(att.content_type) ? (
                    <img
                      key={i}
                      src={`data:${att.content_type};base64,${att.data_base64}`}
                      alt={att.filename}
                      style={{
                        maxWidth: 200,
                        maxHeight: 200,
                        borderRadius: 8,
                        cursor: 'pointer',
                        display: 'block',
                      }}
                      onClick={() => {
                        // Open full-size image in new tab
                        const win = window.open();
                        if (win) {
                          win.document.write(
                            `<img src="data:${att.content_type};base64,${att.data_base64}" style="max-width:100%;height:auto" />`
                          );
                          win.document.title = att.filename;
                        }
                      }}
                      title={`${att.filename} — click to view full size`}
                    />
                  ) : (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                        background: 'rgba(255,255,255,0.15)',
                        borderRadius: 8,
                        padding: '4px 8px',
                        fontSize: 12,
                      }}
                    >
                      <FileText size={14} />
                      <span>{att.filename}</span>
                      <span style={{ opacity: 0.7 }}>
                        ({formatFileSize(att.size_bytes)})
                      </span>
                    </div>
                  ),
                )}
              </div>
            )}
            {message.content.trim() && (
              <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
            )}
          </>
        ) : (
          <>
            {segments!.map((seg, i) =>
              seg.type === 'code' ? (
                <CodeBlock key={i} content={seg.content} />
              ) : (
                <span key={i} dangerouslySetInnerHTML={{ __html: seg.html }} />
              ),
            )}
            {isStreaming && (
              <span className="animate-blink" style={{ marginLeft: 1 }}>
                ▌
              </span>
            )}
          </>
        )}
      </div>

      {!isUser && hasStats && (
        <div style={{ fontSize: 11, color: 'var(--cr-text-dim)', marginTop: 4 }}>
          {(message.tokens!.input + message.tokens!.output).toLocaleString()} tokens
          &nbsp;·&nbsp;${message.cost_usd!.toFixed(4)}
        </div>
      )}
    </div>
  );
}

FILEEOF_frontend_src_components_chat_MessageBubble_tsx
echo '  ✅ frontend/src/components/chat/MessageBubble.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/ModelSelector.tsx' << 'FILEEOF_frontend_src_components_chat_ModelSelector_tsx'
import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronRight, Crown, Sparkles, Zap } from 'lucide-react';
import type { LLMProvider } from '../../types';

// Provider accent colors
const PROVIDER_COLORS: Record<string, string> = {
  openai: '#3E9B5F',
  anthropic: '#F2A41F',
  google: '#4285F4',
  grok: '#D64545',
  deepseek: '#7C8CF5',
  mistral: '#E8853D',
  groq: '#E8853D',
};

const TIER_CONFIG: Record<string, { icon: typeof Crown; color: string }> = {
  top: { icon: Crown, color: '#F2A41F' },
  mid: { icon: Sparkles, color: 'var(--cr-text-dim)' },
  budget: { icon: Zap, color: 'var(--cr-green-600)' },
};

interface ModelSelectorProps {
  providers: LLMProvider[];
  selectedProvider: string | null;
  selectedModel: string | null;
  onSelect: (provider: string, model: string) => void;
  mode: 'grid' | 'compact';
}

function formatPrice(input?: number, output?: number): string {
  if (input == null || output == null) return '';
  if (input < 1) return `$${input.toFixed(2)}/$${output.toFixed(2)}`;
  return `$${input.toFixed(2)}/$${output.toFixed(0)}`;
}

// ── Grid Mode — Collapsible accordions per provider ─────────────

function GridSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  // Track which providers are expanded; default first provider open
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    providers.forEach((p, i) => {
      init[p.id] = i === 0; // first provider open by default
    });
    return init;
  });

  // If selected provider changes, expand it
  useEffect(() => {
    if (selectedProvider) {
      setExpanded((prev) => ({ ...prev, [selectedProvider]: true }));
    }
  }, [selectedProvider]);

  const toggleProvider = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        maxWidth: '700px',
        width: '100%',
      }}
    >
      {providers.map((prov) => {
        const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        const isExpanded = expanded[prov.id] ?? false;
        const hasSelected = selectedProvider === prov.id;

        return (
          <div
            key={prov.id}
            style={{
              background: 'var(--cr-charcoal)',
              borderRadius: 'var(--cr-radius)',
              border: hasSelected ? `1px solid ${accent}40` : '1px solid var(--cr-border)',
              overflow: 'hidden',
              transition: 'border-color 150ms',
            }}
          >
            {/* Provider header — click to expand/collapse */}
            <button
              onClick={() => toggleProvider(prov.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '12px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                transition: 'background 100ms',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--cr-charcoal-deep)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              <div
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: accent,
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--cr-text)',
                  flex: 1,
                  textAlign: 'left',
                  letterSpacing: '0.01em',
                }}
              >
                {prov.name}
              </span>
              <span
                style={{
                  fontSize: '11px',
                  color: 'var(--cr-text-dim)',
                  marginRight: '4px',
                }}
              >
                {prov.models.length} model{prov.models.length !== 1 ? 's' : ''}
              </span>
              {isExpanded ? (
                <ChevronDown
                  style={{ width: 16, height: 16, color: 'var(--cr-text-muted)', transition: 'transform 150ms' }}
                />
              ) : (
                <ChevronRight
                  style={{ width: 16, height: 16, color: 'var(--cr-text-muted)', transition: 'transform 150ms' }}
                />
              )}
            </button>

            {/* Models list — collapsible */}
            {isExpanded && (
              <div style={{ padding: '0 8px 8px' }}>
                {prov.models.map((m) => {
                  const isSelected = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => onSelect(prov.id, m.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        width: '100%',
                        padding: '10px 12px',
                        margin: '2px 0',
                        borderRadius: 'var(--cr-radius-sm)',
                        border: isSelected ? `1px solid ${accent}` : '1px solid transparent',
                        background: isSelected ? `${accent}15` : 'transparent',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 100ms',
                      }}
                      onMouseEnter={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'var(--cr-charcoal-deep)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isSelected) e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      <TierIcon style={{ width: 14, height: 14, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: '13px',
                            fontWeight: isSelected ? 600 : 400,
                            color: isSelected ? 'var(--cr-text)' : 'var(--cr-mist)',
                          }}
                        >
                          {m.name}
                        </div>
                        {m.description && (
                          <div
                            style={{
                              fontSize: '11px',
                              color: 'var(--cr-text-dim)',
                              marginTop: '1px',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                            }}
                          >
                            {m.description}
                          </div>
                        )}
                      </div>
                      {m.context && (
                        <span
                          style={{
                            fontSize: '10px',
                            color: 'var(--cr-text-dim)',
                            background: 'var(--cr-charcoal-deep)',
                            padding: '2px 6px',
                            borderRadius: 'var(--cr-radius-xs)',
                            flexShrink: 0,
                          }}
                        >
                          {m.context}
                        </span>
                      )}
                      <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', flexShrink: 0 }}>
                        {formatPrice(m.input_price, m.output_price)}/1M
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Compact Mode (dropdown in header bar during chat) ────────────

function CompactSelector({
  providers,
  selectedProvider,
  selectedModel,
  onSelect,
}: Omit<ModelSelectorProps, 'mode'>) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isOpen]);

  let selectedModelName = 'Select model';
  let selectedAccent = 'var(--cr-green-600)';
  let selectedContext = '';
  for (const prov of providers) {
    for (const m of prov.models) {
      if (prov.id === selectedProvider && m.id === selectedModel) {
        selectedModelName = m.name;
        selectedAccent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
        selectedContext = m.context || '';
      }
    }
  }

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 14px',
          borderRadius: 'var(--cr-radius-sm)',
          border: '1px solid var(--cr-border)',
          background: 'var(--cr-charcoal)',
          cursor: 'pointer',
          transition: 'all 150ms',
        }}
      >
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: selectedAccent,
          }}
        />
        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--cr-text)' }}>
          {selectedModelName}
        </span>
        {selectedContext && (
          <span style={{ fontSize: '10px', color: 'var(--cr-text-dim)' }}>
            {selectedContext}
          </span>
        )}
        <ChevronDown
          style={{
            width: '14px',
            height: '14px',
            color: 'var(--cr-text-muted)',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
            transition: 'transform 150ms',
          }}
        />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            minWidth: '340px',
            maxHeight: '420px',
            overflowY: 'auto',
            background: 'var(--cr-charcoal-deep)',
            border: '1px solid var(--cr-border)',
            borderRadius: 'var(--cr-radius)',
            padding: '8px',
            zIndex: 50,
            boxShadow: '0 12px 40px rgba(0,0,0,0.5)',
          }}
        >
          {providers.map((prov) => {
            const accent = PROVIDER_COLORS[prov.id] || 'var(--cr-green-600)';
            return (
              <div key={prov.id}>
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: 'var(--cr-text-dim)',
                    padding: '8px 10px 4px',
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                >
                  {prov.name}
                </div>
                {prov.models.map((m) => {
                  const isActive = selectedProvider === prov.id && selectedModel === m.id;
                  const tier = TIER_CONFIG[m.tier] || TIER_CONFIG.mid;
                  const TierIcon = tier.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        onSelect(prov.id, m.id);
                        setIsOpen(false);
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        width: '100%',
                        padding: '8px 10px',
                        borderRadius: 'var(--cr-radius-xs)',
                        border: 'none',
                        background: isActive ? `${accent}15` : 'transparent',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'background 100ms',
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'var(--cr-charcoal)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) (e.currentTarget as HTMLElement).style.background = 'transparent';
                      }}
                    >
                      <TierIcon style={{ width: 13, height: 13, color: tier.color, flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <span
                          style={{
                            fontSize: '13px',
                            fontWeight: isActive ? 500 : 400,
                            color: isActive ? 'var(--cr-text)' : 'var(--cr-mist)',
                          }}
                        >
                          {m.name}
                        </span>
                      </div>
                      {m.context && (
                        <span
                          style={{
                            fontSize: '10px',
                            color: 'var(--cr-text-dim)',
                            background: 'var(--cr-charcoal-deep)',
                            padding: '1px 4px',
                            borderRadius: 'var(--cr-radius-xs)',
                            flexShrink: 0,
                          }}
                        >
                          {m.context}
                        </span>
                      )}
                      <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', flexShrink: 0 }}>
                        {formatPrice(m.input_price, m.output_price)}
                      </span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Export ───────────────────────────────────────────────────────

export default function ModelSelector(props: ModelSelectorProps) {
  return props.mode === 'grid' ? (
    <GridSelector {...props} />
  ) : (
    <CompactSelector {...props} />
  );
}

FILEEOF_frontend_src_components_chat_ModelSelector_tsx
echo '  ✅ frontend/src/components/chat/ModelSelector.tsx'

mkdir -p 'frontend/src/components/chat'
cat > 'frontend/src/components/chat/SpecialistHeader.tsx' << 'FILEEOF_frontend_src_components_chat_SpecialistHeader_tsx'
import type { Specialist } from '../../types';

interface SpecialistHeaderProps {
  specialist: Specialist;
  messageCount: number;
}

export default function SpecialistHeader({ specialist, messageCount }: SpecialistHeaderProps) {
  return (
    <div
      style={{
        height: 56,
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--cr-charcoal)',
        borderBottom: '1px solid var(--cr-border)',
        flexShrink: 0,
      }}
    >
      <div style={{ minWidth: 0, flex: 1, marginRight: 16 }}>
        <div
          style={{
            color: 'var(--cr-text)',
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 600,
            fontSize: 16,
            lineHeight: '20px',
          }}
        >
          {specialist.name}
        </div>
        <div
          style={{
            color: 'var(--cr-text-muted)',
            fontSize: 12,
            marginTop: 2,
            overflow: 'hidden',
            whiteSpace: 'nowrap',
            textOverflow: 'ellipsis',
          }}
        >
          {specialist.description}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
        <span
          style={{
            background: 'var(--cr-charcoal-deep)',
            color: 'var(--cr-text-muted)',
            fontSize: 11,
            padding: '3px 10px',
            borderRadius: 20,
            border: '1px solid var(--cr-border)',
          }}
        >
          {specialist.provider} / {specialist.model}
        </span>
        {messageCount > 0 && (
          <span
            style={{
              background: 'var(--cr-charcoal-deep)',
              color: 'var(--cr-text-muted)',
              fontSize: 11,
              padding: '3px 10px',
              borderRadius: 20,
              border: '1px solid var(--cr-border)',
            }}
          >
            {messageCount} msg{messageCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}

FILEEOF_frontend_src_components_chat_SpecialistHeader_tsx
echo '  ✅ frontend/src/components/chat/SpecialistHeader.tsx'

mkdir -p 'frontend/src/components/pipeline'
cat > 'frontend/src/components/pipeline/AgentTraceVisualizer.tsx' << 'FILEEOF_frontend_src_components_pipeline_AgentTraceVisualizer_tsx'
import { useState, useEffect, useMemo } from 'react';
import { Check, X, ChevronDown, ChevronUp, Clock, Zap, DollarSign, Hash } from 'lucide-react';
import ModelBadge from './ModelBadge';

interface AgentStatus {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  tokens?: { input: number; output: number };
  cost?: number;
  durationMs?: number;
  output?: string;
  model?: string;
}

interface AgentTraceVisualizerProps {
  agents: AgentStatus[];
  status: 'idle' | 'running' | 'complete' | 'error';
  totalCost?: number;
  totalTokens?: number;
  durationMs?: number;
  output?: string;
  error?: string;
}

export default function AgentTraceVisualizer({
  agents,
  status,
  totalCost,
  totalTokens,
  durationMs,
  output,
  error,
}: AgentTraceVisualizerProps) {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [outputExpanded, setOutputExpanded] = useState(false);
  const [runningDots, setRunningDots] = useState(1);

  // Animate running dots
  useEffect(() => {
    if (status !== 'running') return;
    const interval = setInterval(() => {
      setRunningDots(prev => (prev % 3) + 1);
    }, 500);
    return () => clearInterval(interval);
  }, [status]);

  // Calculate max duration for scaling duration bars
  const maxDuration = useMemo(() => {
    const durations = agents
      .filter(a => a.status === 'complete' && a.durationMs)
      .map(a => a.durationMs!);
    return durations.length > 0 ? Math.max(...durations) : 1;
  }, [agents]);

  const completedCount = agents.filter(a => a.status === 'complete').length;
  const runningAgent = agents.find(a => a.status === 'running');

  const toggleAgentExpansion = (agentName: string) => {
    setExpandedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentName)) {
        newSet.delete(agentName);
      } else {
        newSet.add(agentName);
      }
      return newSet;
    });
  };

  const getStatusColor = (agentStatus: string) => {
    switch (agentStatus) {
      case 'complete': return 'var(--cr-green-600)';
      case 'error': return 'var(--cr-danger)';
      case 'running': return 'var(--cr-green-600)';
      default: return 'var(--cr-text-dim)';
    }
  };

  const getStatusNode = (agent: AgentStatus, index: number) => {
    const isRunning = agent.status === 'running';
    const isComplete = agent.status === 'complete';
    const isError = agent.status === 'error';

    return (
      <div
        style={{
          width: '28px',
          height: '28px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
          color: agent.status === 'pending' ? 'var(--cr-text-muted)' : 'var(--cr-text)',
          backgroundColor: isComplete ? 'var(--cr-green-600)' : isError ? 'var(--cr-danger)' : 'transparent',
          border: agent.status === 'pending'
            ? '2px dashed var(--cr-charcoal-deep)'
            : isRunning
              ? '2px solid var(--cr-green-600)'
              : 'none',
          animation: isRunning ? 'animate-pulse-glow' : 'none',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {isComplete && <Check size={14} />}
        {isError && <X size={14} />}
        {agent.status === 'pending' && (index + 1)}
        {isRunning && (index + 1)}
      </div>
    );
  };

  const getConnectorLine = (agent: AgentStatus) => {
    if (agent === agents[agents.length - 1]) return null;

    return (
      <div
        style={{
          width: '2px',
          height: '8px',
          backgroundColor: getStatusColor(agent.status),
          margin: '4px auto 0',
          borderRadius: '1px',
        }}
      />
    );
  };

  const getDurationBar = (durationMs: number) => {
    const percentage = (durationMs / maxDuration) * 100;
    const seconds = (durationMs / 1000).toFixed(1);

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
        <div
          style={{
            width: '80px',
            height: '4px',
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: '100%',
              backgroundColor: 'var(--orange)',
              borderRadius: '2px',
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>{seconds}s</span>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Header bar */}
      <div
        style={{
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '10px',
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: status === 'complete'
                ? 'var(--cr-green-600)'
                : status === 'error'
                  ? 'var(--cr-danger)'
                  : 'var(--cr-green-600)',
              animation: status === 'running' ? 'animate-pulse-glow' : 'none',
            }}
          />
          <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
            {status === 'complete'
              ? 'Pipeline Complete'
              : status === 'error'
                ? 'Pipeline Failed'
                : runningAgent
                  ? `Running: ${runningAgent.name}`
                  : 'Initializing...'}
          </span>
        </div>
        <span style={{ color: 'var(--cr-text-muted)', fontSize: '13px' }}>
          {completedCount} / {agents.length} agents
        </span>
      </div>

      {/* Progress rail */}
      <div
        style={{
          height: '2px',
          backgroundColor: 'var(--cr-charcoal-deep)',
          borderRadius: '1px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${agents.length > 0 ? (completedCount / agents.length) * 100 : 0}%`,
            background: 'linear-gradient(90deg, var(--cr-green-600), var(--cr-green-400))',
            transition: 'width 0.5s ease',
          }}
        />
      </div>

      {/* Agent trace rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {agents.map((agent, index) => (
          <div key={agent.name} style={{ position: 'relative' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
                border: agent.status === 'running' ? '1px solid var(--cr-green-600)' : '1px solid transparent',
              }}
            >
              {getStatusNode(agent, index)}

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--cr-text)', fontSize: '14px', fontWeight: '500' }}>
                    {agent.name}
                  </span>
                  {agent.model && <ModelBadge model={agent.model} />}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                  <span
                    style={{
                      fontSize: '12px',
                      color: agent.status === 'error'
                        ? 'var(--cr-danger)'
                        : agent.status === 'running'
                          ? 'var(--cr-green-400)'
                          : 'var(--cr-text-muted)',
                    }}
                  >
                    {agent.status === 'pending' && 'Waiting'}
                    {agent.status === 'running' && `Processing${'.'.repeat(runningDots)}`}
                    {agent.status === 'error' && 'Failed'}
                    {agent.status === 'complete' && 'Complete'}
                  </span>

                  {agent.status === 'complete' && agent.durationMs && getDurationBar(agent.durationMs)}

                  {agent.status === 'complete' && agent.tokens && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      {(agent.tokens.input + agent.tokens.output).toLocaleString()} tok
                    </span>
                  )}

                  {agent.status === 'complete' && agent.cost !== undefined && (
                    <span style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>
                      ${agent.cost.toFixed(4)}
                    </span>
                  )}

                  {agent.status === 'complete' && agent.output && (
                    <button
                      onClick={() => toggleAgentExpansion(agent.name)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--cr-text-muted)',
                        cursor: 'pointer',
                        padding: '2px',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    >
                      {expandedAgents.has(agent.name) ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  )}
                </div>

                {agent.status === 'complete' && agent.output && expandedAgents.has(agent.name) && (
                  <div
                    style={{
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: 'var(--cr-charcoal-dark)',
                      borderRadius: '6px',
                      borderLeft: '3px solid var(--cr-green-600)',
                      maxHeight: '250px',
                      overflowY: 'auto',
                    }}
                  >
                    <pre
                      style={{
                        margin: 0,
                        fontSize: '12px',
                        color: 'var(--cr-text-muted)',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {agent.output}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {getConnectorLine(agent)}
          </div>
        ))}
      </div>

      {/* Error block */}
      {status === 'error' && error && (
        <div
          style={{
            padding: '12px',
            backgroundColor: 'rgba(192, 57, 43, 0.1)',
            borderRadius: '8px',
            borderLeft: '4px solid var(--cr-danger)',
          }}
        >
          <div style={{ color: 'var(--cr-danger)', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
            Error
          </div>
          <div style={{ color: 'var(--cr-text)', fontSize: '13px' }}>{error}</div>
        </div>
      )}

      {/* Completion summary */}
      {status === 'complete' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '8px',
          }}
        >
          {totalCost !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(45, 139, 78, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <DollarSign size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Cost</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  ${totalCost.toFixed(4)}
                </div>
              </div>
            </div>
          )}

          {totalTokens !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(46, 117, 182, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Hash size={16} color="var(--cr-green-600)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Total Tokens</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {totalTokens.toLocaleString()}
                </div>
              </div>
            </div>
          )}

          {durationMs !== undefined && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                backgroundColor: 'var(--cr-charcoal-deep)',
                borderRadius: '8px',
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(212, 118, 10, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Clock size={16} color="var(--orange)" />
              </div>
              <div>
                <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Duration</div>
                <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                  {(durationMs / 1000).toFixed(1)}s
                </div>
              </div>
            </div>
          )}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px',
              backgroundColor: 'var(--cr-charcoal-deep)',
              borderRadius: '8px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '6px',
                backgroundColor: 'rgba(46, 117, 182, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Zap size={16} color="var(--cr-green-600)" />
            </div>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--cr-text-muted)' }}>Agents</div>
              <div style={{ fontSize: '14px', color: 'var(--cr-text)', fontWeight: '500' }}>
                {completedCount} / {agents.length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Final output block */}
      {status === 'complete' && output && (
        <div
          style={{
            backgroundColor: 'var(--cr-charcoal-deep)',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setOutputExpanded(!outputExpanded)}
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              color: 'var(--cr-text)',
              textAlign: 'left',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            FINAL OUTPUT
            {outputExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {outputExpanded && (
            <div
              style={{
                padding: '0 16px 16px',
                borderTop: '1px solid var(--cr-charcoal-deep)',
              }}
            >
              <pre
                style={{
                  margin: 0,
                  fontSize: '13px',
                  color: 'var(--cr-text-muted)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  lineHeight: '1.5',
                }}
              >
                {output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
FILEEOF_frontend_src_components_pipeline_AgentTraceVisualizer_tsx
echo '  ✅ frontend/src/components/pipeline/AgentTraceVisualizer.tsx'

mkdir -p 'frontend/src/contexts'
cat > 'frontend/src/contexts/AuthContext.tsx' << 'FILEEOF_frontend_src_contexts_AuthContext_tsx'
import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { api } from '../api/client';

interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar_url: string;
  provider: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  login: (email: string) => Promise<void>;
  loginWithOAuth: (provider: 'google' | 'apple' | 'x') => Promise<void>;
  handleOAuthCallback: (provider: string, code: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('fc_token');
    if (token) {
      api.setToken(token);
      // Load user profile
      api.request<UserProfile>('/auth/me')
        .then((profile) => {
          setUser(profile);
          setIsAuthenticated(true);
        })
        .catch(() => {
          // Token expired or invalid
          localStorage.removeItem('fc_token');
          api.setToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }

    // Check for OAuth callback params in URL
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');  // contains provider
    if (code && state) {
      handleOAuthCallback(state, code).then(() => {
        // Clean URL
        window.history.replaceState({}, '', window.location.pathname);
      });
    }
  }, []);

  const _setAuth = (token: string) => {
    api.setToken(token);
    localStorage.setItem('fc_token', token);
    setIsAuthenticated(true);
  };

  const login = async (email: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>('/auth/login', { email });
      _setAuth(response.access_token);
      // Load profile
      const profile = await api.request<UserProfile>('/auth/me');
      setUser(profile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    }
  };

  const loginWithOAuth = async (provider: 'google' | 'apple' | 'x') => {
    setError(null);
    try {
      const response = await api.request<{ auth_url: string }>(`/auth/${provider}`);
      // Redirect to OAuth provider
      window.location.href = response.auth_url;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'OAuth redirect failed';
      setError(message);
      throw err;
    }
  };

  const handleOAuthCallback = async (provider: string, code: string) => {
    setError(null);
    try {
      const response = await api.post<{ access_token: string }>(
        `/auth/${provider}/callback`,
        { code },
      );
      _setAuth(response.access_token);
      const profile = await api.request<UserProfile>('/auth/me');
      setUser(profile);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'OAuth login failed';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.setToken(null);
    localStorage.removeItem('fc_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, isLoading, user, login, loginWithOAuth, handleOAuthCallback, logout, error }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

FILEEOF_frontend_src_contexts_AuthContext_tsx
echo '  ✅ frontend/src/contexts/AuthContext.tsx'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/ChatPage.tsx' << 'FILEEOF_frontend_src_pages_ChatPage_tsx'
import { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronDown, ChevronUp, Bot } from 'lucide-react';
import { api } from '../api/client';
import type { Specialist } from '../types';
import { useChat } from '../hooks/useChat';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import SpecialistHeader from '../components/chat/SpecialistHeader';

const EXAMPLE_PROMPTS: Record<string, string[]> = {
  'financial-analyst': [
    'Analyze the risk profile of a precious metals portfolio',
    'What are the key financial ratios for evaluating a lending company?',
  ],
  'research-assistant': [
    'Compare TILT lending regulations across northeastern states',
    'Summarize recent changes to UCC Article 9',
  ],
  'code-reviewer': [
    'Review this Python function for security vulnerabilities',
    'What are best practices for JWT token rotation?',
  ],
  'legal-quick': [
    'What are the Article I Section 10 implications for precious metals as legal tender?',
    'Outline the key TILA disclosure requirements for consumer lending',
  ],
};

const DEFAULT_PROMPTS = [
  'Help me understand this topic in detail',
  'What are the key considerations for this situation?',
];

export default function ChatPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [selected, setSelected] = useState<Specialist | null>(null);
  const [showSpecialistPanel, setShowSpecialistPanel] = useState(false);

  const { messages, isStreaming, error, sendMessage, stopStreaming } = useChat(
    selected?.id ?? null,
  );

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollPill, setShowScrollPill] = useState(false);

  useEffect(() => {
    api
      .request<{ specialists: Specialist[] }>('/specialists/')
      .then((data) => {
        setSpecialists(data.specialists);
        if (data.specialists.length > 0) setSelected(data.specialists[0]);
      })
      .catch(console.error);
  }, []);

  const isAtBottom = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return true;
    return el.scrollHeight - el.scrollTop - el.clientHeight < 100;
  }, []);

  useEffect(() => {
    if (isAtBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setShowScrollPill(false);
    } else if (messages.length > 0) {
      setShowScrollPill(true);
    }
  }, [messages, isAtBottom]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    setShowScrollPill(false);
  };

  const handleScroll = () => {
    if (isAtBottom()) setShowScrollPill(false);
  };

  const examplePrompts = selected
    ? (EXAMPLE_PROMPTS[selected.id] ?? DEFAULT_PROMPTS)
    : DEFAULT_PROMPTS;

  return (
    <div className="flex" style={{ height: '100vh' }}>
      {/* Desktop specialist sidebar */}
      <div
        className="hidden md:block p-4 overflow-y-auto"
        style={{
          width: 260,
          borderRight: '1px solid var(--cr-border)',
          flexShrink: 0,
          background: 'var(--cr-charcoal)',
        }}
      >
        <h2
          style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--cr-text-dim)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: '12px',
          }}
        >
          Specialists
        </h2>
        {specialists.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            style={{
              width: '100%',
              textAlign: 'left',
              padding: '10px 12px',
              borderRadius: 'var(--cr-radius-sm)',
              marginBottom: '3px',
              border: 'none',
              background: selected?.id === s.id ? 'var(--cr-charcoal-deep)' : 'transparent',
              borderLeft: selected?.id === s.id ? '2px solid var(--cr-green-600)' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 100ms',
            }}
            onMouseEnter={(e) => {
              if (selected?.id !== s.id) e.currentTarget.style.background = 'rgba(42,46,50,0.5)';
            }}
            onMouseLeave={(e) => {
              if (selected?.id !== s.id) e.currentTarget.style.background = 'transparent';
            }}
          >
            <div
              style={{
                fontSize: '13px',
                fontWeight: selected?.id === s.id ? 500 : 400,
                color: selected?.id === s.id ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
              }}
            >
              {s.name}
            </div>
            <div
              style={{
                fontSize: '11px',
                color: 'var(--cr-text-dim)',
                marginTop: '2px',
              }}
            >
              {s.description}
            </div>
          </button>
        ))}
        {specialists.length === 0 && (
          <div style={{ color: 'var(--cr-text-dim)', fontSize: '12px', padding: '8px' }}>
            Loading specialists...
          </div>
        )}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col" style={{ minWidth: 0, overflow: 'hidden' }}>
        {/* Mobile specialist selector */}
        <div className="md:hidden" style={{ borderBottom: '1px solid var(--cr-border)' }}>
          <button
            onClick={() => setShowSpecialistPanel(!showSpecialistPanel)}
            className="w-full flex items-center justify-between px-4 py-3"
            style={{ color: 'var(--cr-text)', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bot style={{ width: 16, height: 16, color: 'var(--cr-green-400)' }} />
              <span style={{ fontSize: '14px', fontWeight: 500 }}>
                {selected?.name ?? 'Select Specialist'}
              </span>
            </div>
            {showSpecialistPanel ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
          {showSpecialistPanel && (
            <div style={{ padding: '0 8px 10px' }}>
              {specialists.map((s) => (
                <button
                  key={s.id}
                  onClick={() => { setSelected(s); setShowSpecialistPanel(false); }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '10px 12px',
                    margin: '2px 0',
                    borderRadius: 'var(--cr-radius-sm)',
                    border: 'none',
                    background: selected?.id === s.id ? 'var(--cr-charcoal-deep)' : 'transparent',
                    borderLeft: selected?.id === s.id ? '2px solid var(--cr-green-600)' : '2px solid transparent',
                    cursor: 'pointer',
                    transition: 'all 100ms',
                  }}
                >
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: selected?.id === s.id ? 500 : 400,
                      color: selected?.id === s.id ? 'var(--cr-green-400)' : 'var(--cr-text-muted)',
                    }}
                  >
                    {s.name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '2px' }}>
                    {s.description}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {selected ? (
          <>
            <div className="hidden md:block">
              <SpecialistHeader specialist={selected} messageCount={messages.length} />
            </div>

            {/* Messages */}
            <div
              ref={scrollContainerRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto"
              style={{ padding: '16px 16px' }}
            >
              {messages.length === 0 ? (
                <div
                  style={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    textAlign: 'center',
                    gap: 12,
                  }}
                >
                  <div
                    style={{
                      width: 48,
                      height: 48,
                      borderRadius: '12px',
                      background: 'var(--cr-green-900)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '4px',
                    }}
                  >
                    <Bot style={{ width: 24, height: 24, color: 'var(--cr-green-400)' }} />
                  </div>
                  <div style={{ color: 'var(--cr-text)', fontSize: '18px', fontWeight: 600 }}>
                    {selected.name}
                  </div>
                  <div style={{ color: 'var(--cr-text-muted)', fontSize: '13px', maxWidth: 400 }}>
                    {selected.description}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginBottom: '12px' }}>
                    Powered by {selected.provider}/{selected.model}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', maxWidth: 500 }}>
                    {examplePrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => sendMessage(prompt)}
                        style={{
                          background: 'var(--cr-charcoal)',
                          border: '1px solid var(--cr-border)',
                          borderRadius: '20px',
                          color: 'var(--cr-text-muted)',
                          fontSize: '12px',
                          padding: '6px 14px',
                          cursor: 'pointer',
                          transition: 'background 200ms, color 200ms',
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal-deep)';
                          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-mist)';
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLButtonElement).style.background = 'var(--cr-charcoal)';
                          (e.currentTarget as HTMLButtonElement).style.color = 'var(--cr-text-muted)';
                        }}
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <MessageBubble
                    key={idx}
                    message={msg}
                    isStreaming={
                      isStreaming && idx === messages.length - 1 && msg.role === 'assistant'
                    }
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {showScrollPill && (
              <div style={{ position: 'relative' }}>
                <button
                  onClick={scrollToBottom}
                  style={{
                    position: 'absolute',
                    bottom: 8,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'var(--cr-green-900)',
                    border: 'none',
                    borderRadius: 20,
                    color: 'var(--cr-text)',
                    fontSize: 12,
                    padding: '5px 14px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4,
                    zIndex: 10,
                  }}
                >
                  <ChevronDown size={14} />
                  New messages
                </button>
              </div>
            )}

            {error && (
              <div
                style={{
                  margin: '0 16px 8px',
                  padding: '8px 12px',
                  background: 'rgba(214, 69, 69, 0.08)',
                  border: '1px solid var(--cr-danger)',
                  borderRadius: 8,
                  color: 'var(--cr-danger)',
                  fontSize: 13,
                }}
              >
                {error}
              </div>
            )}

            <ChatInput
              onSend={sendMessage}
              onStop={stopStreaming}
              isStreaming={isStreaming}
              disabled={false}
              specialistName={selected.name}
            />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p style={{ color: 'var(--cr-text-dim)' }}>Select a specialist to begin</p>
          </div>
        )}
      </div>
    </div>
  );
}

FILEEOF_frontend_src_pages_ChatPage_tsx
echo '  ✅ frontend/src/pages/ChatPage.tsx'

mkdir -p 'frontend/src/pages'
cat > 'frontend/src/pages/LoginPage.tsx' << 'FILEEOF_frontend_src_pages_LoginPage_tsx'
import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, AlertCircle, Mail } from 'lucide-react';

/* ── Social icon SVGs (inline to avoid deps) ─────────────────── */

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}

function AppleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

/* ── Component ───────────────────────────────────────────────── */

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [showEmail, setShowEmail] = useState(false);
  const { login, loginWithOAuth, error } = useAuth();
  const navigate = useNavigate();

  const handleEmailSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email);
      navigate('/');
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'apple' | 'x') => {
    setLoading(true);
    try {
      await loginWithOAuth(provider);
      // OAuth redirects to provider — page will reload on callback
    } catch {
      setLoading(false);
    }
  };

  const btnBase: React.CSSProperties = {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    padding: '12px',
    borderRadius: 'var(--cr-radius-sm)',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 150ms',
    border: 'none',
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ background: 'var(--cr-charcoal-dark)' }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '40px 36px',
          background: 'var(--cr-charcoal)',
          border: '1px solid var(--cr-border)',
          borderRadius: 'var(--cr-radius)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '56px',
              height: '56px',
              borderRadius: '14px',
              background: 'var(--cr-green-900)',
              border: '1px solid var(--cr-green-700)',
              marginBottom: '16px',
            }}
          >
            <Shield style={{ width: '28px', height: '28px', color: 'var(--cr-green-400)' }} />
          </div>
          <h1
            style={{
              fontFamily: "'Space Grotesk', sans-serif",
              fontSize: '22px',
              fontWeight: 700,
              color: 'var(--cr-green-400)',
              letterSpacing: '0.04em',
              margin: '0 0 4px',
            }}
          >
            CALCULUS LABS
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--cr-text-dim)', margin: 0 }}>
            AI Intelligence Portal v2.2
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              borderRadius: 'var(--cr-radius-sm)',
              background: 'rgba(214, 69, 69, 0.1)',
              border: '1px solid rgba(214, 69, 69, 0.25)',
              color: 'var(--cr-danger)',
              fontSize: '13px',
              marginBottom: '16px',
            }}
          >
            <AlertCircle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* OAuth Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
          <button
            onClick={() => handleOAuth('google')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#ffffff',
              color: '#1f1f1f',
            }}
          >
            <GoogleIcon />
            Continue with Google
          </button>

          <button
            onClick={() => handleOAuth('apple')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#000000',
              color: '#ffffff',
            }}
          >
            <AppleIcon />
            Continue with Apple
          </button>

          <button
            onClick={() => handleOAuth('x')}
            disabled={loading}
            style={{
              ...btnBase,
              background: '#14171a',
              color: '#ffffff',
            }}
          >
            <XIcon />
            Continue with X
          </button>
        </div>

        {/* Divider */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            margin: '20px 0',
          }}
        >
          <div style={{ flex: 1, height: '1px', background: 'var(--cr-border)' }} />
          <span style={{ fontSize: '11px', color: 'var(--cr-text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            or
          </span>
          <div style={{ flex: 1, height: '1px', background: 'var(--cr-border)' }} />
        </div>

        {/* Email Login */}
        {!showEmail ? (
          <button
            onClick={() => setShowEmail(true)}
            style={{
              ...btnBase,
              background: 'transparent',
              color: 'var(--cr-text-muted)',
              border: '1px solid var(--cr-border)',
            }}
          >
            <Mail style={{ width: 16, height: 16 }} />
            Continue with email
          </button>
        ) : (
          <form onSubmit={handleEmailSubmit}>
            <label
              style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: 500,
                color: 'var(--cr-text-muted)',
                marginBottom: '8px',
              }}
            >
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@calculusresearch.io"
              required
              autoFocus
              style={{
                width: '100%',
                padding: '12px 16px',
                borderRadius: 'var(--cr-radius-sm)',
                border: '1px solid var(--cr-border)',
                background: 'var(--cr-charcoal-deep)',
                color: 'var(--cr-text)',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 150ms',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'var(--cr-green-600)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'var(--cr-border)';
              }}
            />
            <p style={{ fontSize: '11px', color: 'var(--cr-text-dim)', marginTop: '6px' }}>
              Domain-restricted: @calculusresearch.io or @gradeesolutions.com
            </p>
            <button
              type="submit"
              disabled={loading || !email}
              style={{
                ...btnBase,
                marginTop: '16px',
                background: 'var(--cr-green-900)',
                color: 'var(--cr-green-400)',
                border: '1px solid var(--cr-green-700)',
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 600,
                opacity: loading || !email ? 0.5 : 1,
                cursor: loading || !email ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        )}

        <p
          style={{
            textAlign: 'center',
            fontSize: '11px',
            color: 'var(--cr-text-dim)',
            marginTop: '28px',
          }}
        >
          Calculus Holdings LLC &middot; Secured with JWT authentication
        </p>
      </div>
    </div>
  );
}

FILEEOF_frontend_src_pages_LoginPage_tsx
echo '  ✅ frontend/src/pages/LoginPage.tsx'

mkdir -p 'frontend/src/types'
cat > 'frontend/src/types/index.ts' << 'FILEEOF_frontend_src_types_index_ts'
export interface Specialist {
  id: string;
  name: string;
  description: string;
  provider: string;
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
  version: number;
}

export interface Attachment {
  filename: string;
  content_type: string;     // MIME type: "image/png", "application/pdf", etc.
  data_base64: string;      // base64-encoded file content (no data: URI prefix)
  size_bytes: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  attachments?: Attachment[];   // Files attached to this message (user messages only)
  tokens?: { input: number; output: number };
  cost_usd?: number;
  latency_ms?: number;
}

export interface ChatResponse {
  content: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: number;
}

export interface Pipeline {
  name: string;
  description: string;
  agents: string[];
  estimated_cost: number;
}

export interface PipelineAgent {
  name: string;
  status: 'pending' | 'running' | 'complete' | 'error';
  input_tokens?: number;
  output_tokens?: number;
  cost_usd?: number;
  duration_ms?: number;
  output?: string;
}

export interface PipelineRun {
  pipeline_id: string;
  pipeline_name?: string;
  status: 'running' | 'complete' | 'error';
  agents: PipelineAgent[];
  query: string;
  output?: string;
  total_cost?: number;
  total_tokens?: number;
  duration_ms?: number;
  created_at?: string;
}

// ── Direct LLM Chat ─────────────────────────────────────────────

export interface LLMModel {
  id: string;
  name: string;
  tier: 'top' | 'mid' | 'budget';
  context?: string;
  description?: string;
  input_price: number;
  output_price: number;
}

export interface LLMProvider {
  id: string;
  name: string;
  models: LLMModel[];
}

export interface LLMModelsResponse {
  providers: LLMProvider[];
}

// ── Usage ───────────────────────────────────────────────────────

export interface UsageLog {
  id: number;
  user_hash: string;
  timestamp: string;
  provider: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  latency_ms: number;
  specialist_id?: string;
}

// ── Conversations ────────────────────────────────────────────────

export interface ConversationSummary {
  uuid: string;
  title: string;
  provider: string;
  model: string;
  mode: string;
  specialist_id?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
  preview: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

FILEEOF_frontend_src_types_index_ts
echo '  ✅ frontend/src/types/index.ts'

mkdir -p '.'
cat > 'requirements.txt' << 'FILEEOF_requirements_txt'
anthropic>=0.79.0
google-generativeai>=0.4.0
nest-asyncio>=1.6.0
openai~=1.83.0
pdfplumber>=0.11.0
pytest>=7.0
pytest-asyncio>=0.23.0
pytest-cov>=4.0
python-dotenv>=1.0.0
streamlit>=1.30.0
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
websockets>=12.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
sqlmodel>=0.0.22
psycopg2-binary>=2.9.9
crewai>=0.80.0
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-anthropic>=0.2.0
langchain-google-genai>=2.0.0
requests>=2.31.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
PyYAML>=6.0
litellm>=1.40.0
google-genai>=1.0.0
httpx>=0.27.0

FILEEOF_requirements_txt
echo '  ✅ requirements.txt'


echo ""
echo "📦 Staging and committing..."
git add -A
git status --short
git commit --no-gpg-sign -m "v2.2: OAuth login, conversation history, collapsible model selector, CR design tokens

Backend: User/Conversation/Message tables, Google/Apple/X OAuth handlers,
conversation CRUD with auto-titling, /auth/me endpoint, httpx added.

Frontend: OAuth login page (Google/Apple/X + email), AuthContext with OAuth
flow, ConversationList sidebar, collapsible provider accordions on main page,
specialists-only on specialist page, full CR design token alignment.

All components use var(--cr-*) tokens. Zero stale hex." || echo "Nothing to commit"

echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Done! Now SSH to VM and run:"
echo "  cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main"
echo "  sudo docker compose -f docker-compose.v2.yml build --no-cache backend frontend"
echo "  sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
