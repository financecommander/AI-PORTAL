"""Token bucket rate limiter middleware for FastAPI."""

import time
import threading
from collections import defaultdict, OrderedDict
from typing import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.settings import settings


class TokenBucketRateLimiter:
    """Token bucket rate limiter with thread safety and memory management."""
    
    def __init__(self, capacity: int, refill_rate: float, max_buckets: int = 10000):
        """
        Initialize rate limiter.
        
        Args:
            capacity: Maximum number of tokens in bucket (max requests)
            refill_rate: Tokens added per second
            max_buckets: Maximum number of buckets to keep in memory (LRU eviction)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.max_buckets = max_buckets
        self.buckets: OrderedDict[str, dict] = OrderedDict()
        self.lock = threading.Lock()
    
    def _refill(self, bucket: dict) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(
            self.capacity,
            bucket["tokens"] + elapsed * self.refill_rate
        )
        bucket["last_refill"] = now
    
    def _evict_old_buckets(self) -> None:
        """Remove oldest buckets if we exceed max_buckets limit."""
        while len(self.buckets) > self.max_buckets:
            self.buckets.popitem(last=False)  # Remove oldest (FIFO)
    
    def consume(self, key: str, tokens: int = 1) -> tuple[bool, dict]:
        """
        Try to consume tokens from bucket (thread-safe).
        
        Args:
            key: Identifier for the bucket (e.g., user ID, IP address)
            tokens: Number of tokens to consume
            
        Returns:
            Tuple of (success, info_dict) where info_dict contains:
                - remaining: tokens remaining
                - limit: total capacity
                - reset: seconds until bucket is full
        """
        with self.lock:
            # Get or create bucket
            if key not in self.buckets:
                self.buckets[key] = {
                    "tokens": self.capacity,
                    "last_refill": time.time()
                }
                self._evict_old_buckets()
            else:
                # Move to end (mark as recently used)
                self.buckets.move_to_end(key)
            
            bucket = self.buckets[key]
            self._refill(bucket)
            
            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                success = True
            else:
                success = False
            
            # Calculate time until bucket is full
            tokens_needed = self.capacity - bucket["tokens"]
            reset_seconds = tokens_needed / self.refill_rate if self.refill_rate > 0 else 0
            
            info = {
                "remaining": int(bucket["tokens"]),
                "limit": self.capacity,
                "reset": int(reset_seconds)
            }
            
            return success, info


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to requests."""
    
    def __init__(self, app, capacity: int = None, window_seconds: int = None):
        super().__init__(app)
        capacity = capacity or settings.RATE_LIMIT_REQUESTS
        window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        refill_rate = capacity / window_seconds
        self.limiter = TokenBucketRateLimiter(capacity, refill_rate)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to request."""
        # TODO: Extract user ID from JWT token for per-user rate limiting
        # For now, use client IP with X-Forwarded-For support
        client_id = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_id:
            client_id = request.client.host if request.client else "unknown"
        
        # Try to consume a token
        allowed, info = self.limiter.consume(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {info['reset']} seconds.",
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"])
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response
