"""In-memory token bucket rate limiter."""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.auth.jwt_handler import decode_access_token

EXEMPT_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
RATE_LIMIT = 60
WINDOW_SECONDS = 3600
# Stricter limit for login to prevent brute-force attacks
LOGIN_RATE_LIMIT = 10
LOGIN_WINDOW_SECONDS = 900  # 15 minutes


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._login_buckets: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # IP-based rate limiting for login (no auth token available yet)
        if path.startswith("/auth/login") or path.startswith("/auth/oauth"):
            client_ip = request.headers.get("x-real-ip") or request.client.host if request.client else "unknown"
            now = time.time()
            window_start = now - LOGIN_WINDOW_SECONDS
            try:
                self._login_buckets[client_ip] = [
                    t for t in self._login_buckets[client_ip] if t > window_start
                ]
                if len(self._login_buckets[client_ip]) >= LOGIN_RATE_LIMIT:
                    return JSONResponse(
                        status_code=429,
                        content={"error": "Too many login attempts. Try again later."},
                        headers={"Retry-After": str(LOGIN_WINDOW_SECONDS)},
                    )
                self._login_buckets[client_ip].append(now)
            except Exception:
                pass
            return await call_next(request)

        if path in EXEMPT_PATHS:
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

        try:
            self._buckets[user_key] = [t for t in self._buckets[user_key] if t > window_start]
            remaining = RATE_LIMIT - len(self._buckets[user_key])

            if remaining <= 0:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded"},
                    headers={"X-RateLimit-Limit": str(RATE_LIMIT), "X-RateLimit-Remaining": "0"},
                )

            self._buckets[user_key].append(now)
        except Exception:
            return await call_next(request)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining - 1, 0))
        return response