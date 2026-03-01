"""Authentication routes — email + OAuth (Google, Apple, X) with refresh tokens.

Security:
- All OAuth callbacks require a valid HMAC-signed state token (CSRF protection).
- X/Twitter uses PKCE S256 with a per-flow cryptographic code_verifier.
"""

import logging
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from backend.auth.authenticator import get_current_user
from backend.auth.jwt_handler import create_refresh_token, decode_refresh_token
from backend.auth.oauth import (
    google_get_auth_url, google_exchange_code,
    apple_get_auth_url, apple_exchange_code,
    x_get_auth_url, x_exchange_code,
    get_or_create_user, create_user_token,
)
from backend.auth.oauth_state import validate_oauth_state
from backend.models import User

logger = logging.getLogger(__name__)

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
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str


def _make_refresh(user: User) -> str:
    """Build a refresh token from a User model."""
    return create_refresh_token({
        "sub": str(user.id),
        "email": user.email,
        "provider": user.oauth_provider,
    })


# ── Email login (domain-restricted) ────────────────────────────


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    email = request.email
    domain = email.split("@")[1]
    if domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=401, detail="Email domain is not authorized")
    user = get_or_create_user(email=email, oauth_provider="email")
    return LoginResponse(
        access_token=create_user_token(user),
        refresh_token=_make_refresh(user),
    )


# ── Token refresh ──────────────────────────────────────────────


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshRequest):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    payload = decode_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = get_or_create_user(
        email=payload.get("email", ""),
        oauth_provider=payload.get("provider", "email"),
    )
    return LoginResponse(
        access_token=create_user_token(user),
        refresh_token=_make_refresh(user),
    )


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
    url, _state = await google_get_auth_url()
    return {"auth_url": url}


@router.post("/google/callback", response_model=LoginResponse)
async def google_callback(request: OAuthCallbackRequest):
    payload = validate_oauth_state(request.state, "google")
    if not payload:
        logger.warning("Google OAuth: invalid or expired state token")
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    user = await google_exchange_code(request.code)
    if not user:
        raise HTTPException(status_code=401, detail="Google authentication failed")
    return LoginResponse(access_token=create_user_token(user), refresh_token=_make_refresh(user))


# ── Apple OAuth ─────────────────────────────────────────────────


@router.get("/apple")
async def apple_auth():
    url, _state = await apple_get_auth_url()
    return {"auth_url": url}


@router.post("/apple/callback", response_model=LoginResponse)
async def apple_callback(request: OAuthCallbackRequest):
    payload = validate_oauth_state(request.state, "apple")
    if not payload:
        logger.warning("Apple OAuth: invalid or expired state token")
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    user = await apple_exchange_code(request.code)
    if not user:
        raise HTTPException(status_code=401, detail="Apple authentication failed")
    return LoginResponse(access_token=create_user_token(user), refresh_token=_make_refresh(user))


# ── X (Twitter) OAuth ───────────────────────────────────────────


@router.get("/x")
async def x_auth():
    url, _state = await x_get_auth_url()
    return {"auth_url": url}


@router.post("/x/callback", response_model=LoginResponse)
async def x_callback(request: OAuthCallbackRequest):
    payload = validate_oauth_state(request.state, "x")
    if not payload:
        logger.warning("X OAuth: invalid or expired state token")
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    # Extract the PKCE code_verifier from the signed state token
    code_verifier = payload.get("v", "")
    if not code_verifier:
        logger.error("X OAuth: state token missing code_verifier")
        raise HTTPException(status_code=400, detail="Invalid OAuth state (missing PKCE verifier)")
    user = await x_exchange_code(request.code, code_verifier)
    if not user:
        raise HTTPException(status_code=401, detail="X authentication failed")
    return LoginResponse(access_token=create_user_token(user), refresh_token=_make_refresh(user))

