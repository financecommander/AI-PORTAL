"""In-memory token blacklist for session revocation.

When a user logs out, their access and refresh token JTIs (JWT IDs)
are added to the blacklist. Entries auto-expire after the token's
max lifetime (7 days for refresh tokens) to prevent unbounded growth.

For a single-instance deployment this is sufficient. For multi-instance,
swap to Redis or a DB table.
"""

import hashlib
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Max TTL = refresh token lifetime (7 days) + 1 hour buffer
_MAX_TTL = 7 * 24 * 3600 + 3600

# {token_hash: expiry_timestamp}
_blacklist: dict[str, float] = {}
_lock = threading.Lock()

# Cleanup runs at most once per hour
_last_cleanup: float = 0.0
_CLEANUP_INTERVAL = 3600


def _token_hash(token: str) -> str:
    """SHA-256 hash of the raw token string.

    We store hashes instead of raw tokens so the blacklist doesn't
    become a target for token theft.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _maybe_cleanup() -> None:
    """Remove expired entries if enough time has passed."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    expired = [k for k, exp in _blacklist.items() if exp < now]
    for k in expired:
        del _blacklist[k]
    if expired:
        logger.debug("Token blacklist cleanup: removed %d expired entries", len(expired))


def revoke_token(token: str, ttl: int | None = None) -> None:
    """Add a token to the blacklist.

    Args:
        token: The raw JWT string.
        ttl: Seconds until the blacklist entry expires.
             Defaults to _MAX_TTL (7 days + 1h).
    """
    h = _token_hash(token)
    expiry = time.time() + (ttl if ttl is not None else _MAX_TTL)
    with _lock:
        _blacklist[h] = expiry
        _maybe_cleanup()


def is_revoked(token: str) -> bool:
    """Check if a token has been revoked (blacklisted)."""
    h = _token_hash(token)
    with _lock:
        expiry = _blacklist.get(h)
    if expiry is None:
        return False
    if expiry < time.time():
        # Entry expired — remove it
        with _lock:
            _blacklist.pop(h, None)
        return False
    return True
