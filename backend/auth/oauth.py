"""OAuth authentication handlers for Google, Apple, and X (Twitter).

Lightweight implementation using direct HTTP calls to OAuth providers.
No heavy dependencies — just httpx for async HTTP.

Security:
- All providers use HMAC-signed state tokens for CSRF protection.
- X/Twitter uses proper PKCE (S256) with cryptographic code_verifier.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timezone
from urllib.parse import quote

import httpx
from jose import jwt as jose_jwt, JWTError
from sqlmodel import Session, select

from backend.database import engine
from backend.models import User
from backend.auth.jwt_handler import create_access_token
from backend.auth.oauth_state import create_oauth_state, generate_pkce_pair

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


async def google_get_auth_url() -> tuple[str, str]:
    """Get Google OAuth authorization URL with signed state token.

    Returns (auth_url, state_token).
    """
    redirect_uri = _get_redirect_uri("google")
    state = create_oauth_state("google")
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=openid+email+profile&"
        "access_type=offline&"
        "prompt=consent&"
        f"state={quote(state, safe='')}"
    )
    return url, state


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


# ── Apple JWKS cache for id_token verification ─────────────────

_apple_jwks: dict = {}
_apple_jwks_fetched: float = 0.0
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_JWKS_TTL = 3600  # re-fetch keys every hour


async def _get_apple_jwks() -> dict:
    """Fetch and cache Apple's public JWKS keys for id_token verification."""
    global _apple_jwks, _apple_jwks_fetched
    import time
    now = time.time()
    if _apple_jwks and (now - _apple_jwks_fetched) < APPLE_JWKS_TTL:
        return _apple_jwks
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(APPLE_JWKS_URL, timeout=10)
            if resp.status_code == 200:
                _apple_jwks = resp.json()
                _apple_jwks_fetched = now
                logger.info("Refreshed Apple JWKS keys (%d keys)", len(_apple_jwks.get("keys", [])))
            else:
                logger.error("Failed to fetch Apple JWKS: %s", resp.status_code)
    except Exception:
        logger.error("Error fetching Apple JWKS", exc_info=True)
    return _apple_jwks


async def _verify_apple_id_token(id_token: str) -> Optional[dict]:
    """Verify Apple id_token JWT signature using Apple's public JWKS keys.

    Returns the decoded payload or None if verification fails.
    Validates: signature, issuer (appleid.apple.com), audience (our client_id).
    """
    jwks = await _get_apple_jwks()
    if not jwks or "keys" not in jwks:
        logger.error("Apple JWKS not available; cannot verify id_token")
        return None

    try:
        # python-jose will match the token's 'kid' header against the JWKS
        payload = jose_jwt.decode(
            id_token,
            jwks,
            algorithms=["RS256"],
            audience=APPLE_CLIENT_ID,
            issuer="https://appleid.apple.com",
        )
        return payload
    except JWTError as e:
        logger.error("Apple id_token verification failed: %s", e)
        return None


# ── Apple OAuth ─────────────────────────────────────────────────


async def apple_get_auth_url() -> tuple[str, str]:
    """Get Apple Sign In authorization URL with signed state token.

    Returns (auth_url, state_token).
    """
    redirect_uri = _get_redirect_uri("apple")
    state = create_oauth_state("apple")
    url = (
        "https://appleid.apple.com/auth/authorize?"
        f"client_id={APPLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "response_type=code&"
        "scope=name+email&"
        "response_mode=form_post&"
        f"state={quote(state, safe='')}"
    )
    return url, state


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
        id_token = tokens.get("id_token", "")
        if not id_token:
            logger.error("Apple auth: no id_token in response")
            return None

        # Verify id_token signature against Apple's JWKS public keys
        payload = await _verify_apple_id_token(id_token)
        if not payload:
            return None

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


async def x_get_auth_url() -> tuple[str, str]:
    """Get X OAuth 2.0 authorization URL with real PKCE (S256) and signed state.

    Returns (auth_url, state_token).
    The code_verifier is embedded inside the signed state token so it can
    be recovered during the callback without server-side session storage.
    """
    redirect_uri = _get_redirect_uri("x")
    verifier, challenge = generate_pkce_pair()
    state = create_oauth_state("x", code_verifier=verifier)
    url = (
        "https://twitter.com/i/oauth2/authorize?"
        "response_type=code&"
        f"client_id={X_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "scope=tweet.read+users.read+offline.access&"
        f"state={quote(state, safe='')}&"
        f"code_challenge={challenge}&"
        "code_challenge_method=S256"
    )
    return url, state


async def x_exchange_code(code: str, code_verifier: str) -> Optional[User]:
    """Exchange X auth code for user info using the real PKCE code_verifier."""
    redirect_uri = _get_redirect_uri("x")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "code": code,
                "client_id": X_CLIENT_ID,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
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

