"""OAuth state token management — CSRF protection + PKCE code verifiers.

State tokens are HMAC-signed, time-limited, and contain:
- provider:  which OAuth provider (google, apple, x)
- nonce:     random bytes to prevent replay
- verifier:  PKCE code_verifier (X/Twitter only, empty for others)
- exp:       expiration timestamp (10 minutes)

Wire format:  {provider}:{base64_payload}.{hmac_hex}
The provider prefix lets the frontend extract the provider name
without needing to decode the signed portion.
"""

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# State tokens expire after 10 minutes (plenty for an OAuth round-trip)
STATE_TTL_SECONDS = 600


# ── PKCE helpers ─────────────────────────────────────────────────


def generate_pkce_pair() -> tuple[str, str]:
    """Generate a PKCE code_verifier and S256 code_challenge.

    Returns (code_verifier, code_challenge).
    The verifier is 43 URL-safe characters (~256 bits of entropy).
    The challenge is the base64url-encoded SHA-256 of the verifier.
    """
    verifier = secrets.token_urlsafe(32)  # 43 chars
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


# ── State token creation / validation ────────────────────────────


def _sign(data: bytes) -> str:
    """HMAC-SHA256 hex signature using the app's JWT secret."""
    return hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        data,
        hashlib.sha256,
    ).hexdigest()


def create_oauth_state(provider: str, code_verifier: str = "") -> str:
    """Create a signed, time-limited OAuth state token.

    Returns a string in the format:  {provider}:{base64_payload}.{hmac_hex}
    """
    payload = {
        "p": provider,
        "n": secrets.token_hex(16),
        "v": code_verifier,
        "exp": int(time.time()) + STATE_TTL_SECONDS,
    }
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sig = _sign(data)
    token = base64.urlsafe_b64encode(data).decode("ascii") + "." + sig
    return f"{provider}:{token}"


def validate_oauth_state(state: str, expected_provider: str) -> Optional[dict]:
    """Validate an OAuth state token.

    Returns the decoded payload dict if valid, or None if:
    - format is wrong
    - HMAC signature doesn't match
    - token is expired
    - provider doesn't match expected_provider

    The returned dict has keys: p (provider), n (nonce), v (verifier), exp.
    """
    # Split provider prefix
    colon_idx = state.find(":")
    if colon_idx < 1:
        logger.warning("OAuth state: missing provider prefix")
        return None

    prefix = state[:colon_idx]
    token = state[colon_idx + 1:]

    if prefix != expected_provider:
        logger.warning("OAuth state: provider prefix mismatch (%s != %s)", prefix, expected_provider)
        return None

    # Split payload.signature
    dot_idx = token.rfind(".")
    if dot_idx < 1:
        logger.warning("OAuth state: missing signature separator")
        return None

    data_b64 = token[:dot_idx]
    sig = token[dot_idx + 1:]

    try:
        data = base64.urlsafe_b64decode(data_b64)
    except Exception:
        logger.warning("OAuth state: base64 decode failed")
        return None

    # Verify HMAC
    expected_sig = _sign(data)
    if not hmac.compare_digest(sig, expected_sig):
        logger.warning("OAuth state: HMAC signature mismatch")
        return None

    # Decode JSON payload
    try:
        payload = json.loads(data)
    except Exception:
        logger.warning("OAuth state: JSON decode failed")
        return None

    # Check expiration
    if payload.get("exp", 0) < time.time():
        logger.warning("OAuth state: token expired")
        return None

    # Verify inner provider matches
    if payload.get("p") != expected_provider:
        logger.warning("OAuth state: inner provider mismatch")
        return None

    return payload
