"""In-memory token bucket rate limiter."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.auth.jwt_handler import decode_access_token

EXEMPT_PATHS = {"/", "/health", "/auth/login", "/docs", "/openapi.json", "/redoc"}
RATE_LIMIT = 60  # requests per window
WINDOW_SECONDS = 3600  # 1 hour


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return await call_next(request)

        try:
            token = auth.split(" ", 1)[1]
            payload = decode_access_token(token)
            if not payload:
                return await call_next(request)
            user_key = payload.get("sub", "unknown")
        except Exception:
            return await call_next(request)

        now = time.time()
        window_start = now - WINDOW_SECONDS
        self._buckets.setdefault(user_key, [])
        self._buckets[user_key] = [t for t in self._buckets[user_key] if t > window_start]
        if not self._buckets[user_key]:
            del self._buckets[user_key]
            remaining = RATE_LIMIT
        else:
            remaining = RATE_LIMIT - len(self._buckets[user_key])

        if remaining <= 0:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={"X-RateLimit-Limit": str(RATE_LIMIT), "X-RateLimit-Remaining": "0"},
            )

        self._buckets[user_key].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        return response
