"""Token-bucket rate limiter for FinanceCommander AI Portal."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from config.settings import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


@dataclass
class TokenBucket:
    """Sliding-window token bucket rate limiter.

    Capacity tokens are refilled over *window_seconds*.
    Each ``consume()`` call removes one token; if no tokens remain the
    call returns False and ``retry_after_seconds`` indicates when the
    next token will be available.
    """

    capacity: int = RATE_LIMIT_REQUESTS
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS
    tokens: float = field(init=False)
    _last_refill: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)
        self._last_refill = time.time()

    # -- public API --

    def consume(self, n: int = 1) -> bool:
        """Try to consume *n* tokens. Returns True on success."""
        self._refill()
        if self.tokens >= n:
            self.tokens -= n
            return True
        return False

    @property
    def remaining(self) -> int:
        """Number of tokens currently available (after refill)."""
        self._refill()
        return int(self.tokens)

    @property
    def retry_after_seconds(self) -> int:
        """Seconds until the next token becomes available."""
        if self.tokens >= 1:
            return 0
        refill_rate = self.capacity / self.window_seconds  # tokens/sec
        deficit = 1.0 - self.tokens
        return max(1, int(deficit / refill_rate) + 1)

    # -- internals --

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self._last_refill
        if elapsed <= 0:
            return
        refill_rate = self.capacity / self.window_seconds
        self.tokens = min(self.capacity, self.tokens + elapsed * refill_rate)
        self._last_refill = now


def get_rate_limiter() -> TokenBucket:
    """Return the per-session TokenBucket from Streamlit session state.

    Creates one if it doesn't exist yet.  Safe to call from test code
    that doesn't use Streamlit by monkey-patching ``st.session_state``.
    """
    try:
        import streamlit as st

        if "portal_rate_bucket" not in st.session_state:
            st.session_state["portal_rate_bucket"] = TokenBucket()
        return st.session_state["portal_rate_bucket"]
    except Exception:
        # Fallback for non-Streamlit contexts (tests)
        return TokenBucket()
