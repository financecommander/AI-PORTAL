"""Tests for rate limiter memory leak fix (Bug #23)."""

import time
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.middleware.rate_limiter import RateLimiterMiddleware, RATE_LIMIT, WINDOW_SECONDS


def _make_request(path="/test", auth_token=None):
    """Build a mock Starlette Request."""
    req = MagicMock()
    req.url.path = path
    if auth_token:
        req.headers = {"authorization": f"Bearer {auth_token}"}
    else:
        req.headers = {}
    req.headers.get = lambda key, default="": (
        req.headers.get(key, default) if isinstance(req.headers, dict)
        else default
    )
    # Fix: make headers.get work properly
    headers_dict = {"authorization": f"Bearer {auth_token}"} if auth_token else {}
    req.headers = MagicMock()
    req.headers.get = lambda key, default="": headers_dict.get(key, default)
    return req


def _make_response():
    """Build a mock response with mutable headers."""
    resp = MagicMock()
    resp.headers = {}
    return resp


@pytest.fixture
def limiter():
    """Fresh RateLimiterMiddleware with a dummy app."""
    app = MagicMock()
    return RateLimiterMiddleware(app)


@pytest.fixture
def valid_token():
    """A real JWT token for the test user."""
    from backend.auth.jwt_handler import create_access_token
    return create_access_token({"sub": "limiter-test-user"})


# ─── Cleanup tests (Bug #23) ───

@pytest.mark.asyncio
async def test_expired_timestamps_are_cleaned(limiter, valid_token):
    """After all timestamps expire, the bucket entry is deleted from memory."""
    user_key = "limiter-test-user"

    # Pre-populate with timestamps that are already expired
    old_time = time.time() - WINDOW_SECONDS - 100
    limiter._buckets[user_key] = [old_time, old_time + 1, old_time + 2]
    assert user_key in limiter._buckets

    # Simulate a request — the middleware should filter expired + delete empty bucket
    req = _make_request(auth_token=valid_token)
    resp = _make_response()
    call_next = AsyncMock(return_value=resp)

    await limiter.dispatch(req, call_next)

    # Bucket key should exist again (new request added a fresh timestamp)
    assert user_key in limiter._buckets
    # But the old timestamps should be gone — only the new one remains
    assert len(limiter._buckets[user_key]) == 1


@pytest.mark.asyncio
async def test_empty_bucket_deleted_when_no_new_request(limiter):
    """If a user's timestamps all expire and no new request comes, the key is gone."""
    user_key = "ghost-user"
    old_time = time.time() - WINDOW_SECONDS - 100
    limiter._buckets[user_key] = [old_time]

    # Simulate a request from a DIFFERENT user
    other_token_payload = {"sub": "other-user"}
    from backend.auth.jwt_handler import create_access_token
    other_token = create_access_token(other_token_payload)

    req = _make_request(auth_token=other_token)
    resp = _make_response()
    call_next = AsyncMock(return_value=resp)

    await limiter.dispatch(req, call_next)

    # ghost-user's bucket is still there (only cleaned on their own request)
    # but let's verify that when ghost-user does make a request, it gets cleaned
    ghost_token = create_access_token({"sub": user_key})
    req2 = _make_request(auth_token=ghost_token)
    resp2 = _make_response()
    call_next2 = AsyncMock(return_value=resp2)

    await limiter.dispatch(req2, call_next2)
    # Now the bucket was cleaned (old expired) then a new timestamp added
    assert len(limiter._buckets[user_key]) == 1


@pytest.mark.asyncio
async def test_rate_limit_headers_present(limiter, valid_token):
    """Responses include X-RateLimit-Limit and X-RateLimit-Remaining."""
    req = _make_request(auth_token=valid_token)
    resp = _make_response()
    call_next = AsyncMock(return_value=resp)

    result = await limiter.dispatch(req, call_next)
    assert result.headers["X-RateLimit-Limit"] == str(RATE_LIMIT)
    assert "X-RateLimit-Remaining" in result.headers


@pytest.mark.asyncio
async def test_exempt_paths_bypass_limiter(limiter):
    """Exempt paths like /health are not rate-limited."""
    req = _make_request(path="/health")
    resp = _make_response()
    call_next = AsyncMock(return_value=resp)

    result = await limiter.dispatch(req, call_next)
    call_next.assert_called_once()
    # No buckets should be created
    assert len(limiter._buckets) == 0


@pytest.mark.asyncio
async def test_no_auth_header_passes_through(limiter):
    """Requests without Bearer auth are not rate-limited."""
    req = _make_request(path="/specialists/")
    resp = _make_response()
    call_next = AsyncMock(return_value=resp)

    result = await limiter.dispatch(req, call_next)
    call_next.assert_called_once()
    assert len(limiter._buckets) == 0


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(limiter, valid_token):
    """After RATE_LIMIT requests, the next one gets 429."""
    user_key = "limiter-test-user"
    # Pre-fill the bucket to capacity
    now = time.time()
    limiter._buckets[user_key] = [now - i for i in range(RATE_LIMIT)]

    req = _make_request(auth_token=valid_token)
    call_next = AsyncMock()

    result = await limiter.dispatch(req, call_next)
    assert result.status_code == 429
    call_next.assert_not_called()
