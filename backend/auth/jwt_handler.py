"""JWT authentication handler — access + refresh tokens."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from backend.config.settings import settings

# Refresh tokens live 7 days; access tokens use settings.jwt_expiration_hours (default 24h)
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a short-lived JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.jwt_expiration_hours)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token (7 days).

    Only carries the minimal claims needed to issue a new access token
    (sub, email, provider) — no permissions or profile data.
    """
    to_encode = {
        "sub": data.get("sub"),
        "email": data.get("email", ""),
        "provider": data.get("provider", "email"),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token.

    Returns the payload dict or ``None`` if the token is invalid/expired.
    Rejects refresh tokens used as access tokens.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        # Reject refresh tokens presented as access tokens
        if payload.get("type") == "refresh":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT refresh token.

    Returns the payload dict or ``None`` if the token is invalid/expired
    or is not a refresh token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
