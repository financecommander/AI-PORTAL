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

