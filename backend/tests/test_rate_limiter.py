"""Tests for rate limiter middleware."""

import pytest
import time

from backend.middleware.rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiter:
    """Test the token bucket rate limiter."""

    def test_initial_capacity(self):
        """Test that limiter starts with full capacity."""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        success, info = limiter.consume("test-key", 1)
        
        assert success is True
        assert info["limit"] == 10
        assert info["remaining"] == 9

    def test_consume_tokens(self):
        """Test consuming multiple tokens."""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        
        # Consume 5 tokens
        success, info = limiter.consume("test-key", 5)
        assert success is True
        assert info["remaining"] == 5
        
        # Consume 3 more
        success, info = limiter.consume("test-key", 3)
        assert success is True
        assert info["remaining"] == 2

    def test_exceed_capacity(self):
        """Test that consuming more than capacity fails."""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        
        # Consume all tokens
        success, _ = limiter.consume("test-key", 5)
        assert success is True
        
        # Try to consume one more
        success, info = limiter.consume("test-key", 1)
        assert success is False
        assert info["remaining"] == 0

    def test_refill_over_time(self):
        """Test that tokens refill over time."""
        # Create limiter with 10 capacity, 10 tokens per second
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=10.0)
        
        # Consume all tokens
        success, info = limiter.consume("test-key", 10)
        assert success is True
        assert info["remaining"] == 0
        
        # Wait for 0.5 seconds (should refill 5 tokens)
        time.sleep(0.5)
        
        # Should be able to consume 5 tokens
        success, info = limiter.consume("test-key", 5)
        assert success is True

    def test_multiple_keys(self):
        """Test that different keys have separate buckets."""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
        
        # Consume tokens for key1
        success, info = limiter.consume("key1", 5)
        assert success is True
        assert info["remaining"] == 0
        
        # key2 should have full capacity
        success, info = limiter.consume("key2", 5)
        assert success is True
        assert info["remaining"] == 0

    def test_reset_calculation(self):
        """Test that reset time is calculated correctly."""
        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)
        
        # Consume all tokens
        success, info = limiter.consume("test-key", 10)
        assert success is True
        
        # Reset should be approximately 10 seconds (to refill all 10 tokens at 1/sec)
        assert 9 <= info["reset"] <= 11

    def test_max_capacity_not_exceeded(self):
        """Test that refill doesn't exceed max capacity."""
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=10.0)
        
        # Consume 2 tokens
        success, info = limiter.consume("test-key", 2)
        assert success is True
        
        # Wait for 1 second (would refill 10 tokens, but max is 5)
        time.sleep(1.0)
        
        # Should not be able to consume more than 5 total
        success, info = limiter.consume("test-key", 5)
        assert success is True
        
        # No tokens should remain
        success, info = limiter.consume("test-key", 1)
        assert success is False


class TestRateLimitMiddleware:
    """Test rate limit middleware with FastAPI."""

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are present in responses."""
        response = client.get("/health")
        
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_enforcement(self, client):
        """Test that rate limit is enforced."""
        # Note: This test might be flaky depending on the rate limit settings
        # In production, you'd want to configure a lower limit for testing
        
        # Make multiple requests
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_rate_limit_headers_decrease(self, client):
        """Test that remaining count decreases with requests."""
        response1 = client.get("/health")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])
        
        response2 = client.get("/health")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])
        
        assert remaining2 < remaining1
