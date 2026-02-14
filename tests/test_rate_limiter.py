"""Tests for the token-bucket rate limiter."""

import time

import pytest

from auth.rate_limiter import TokenBucket


class TestTokenBucket:
    def test_initial_capacity(self):
        bucket = TokenBucket(capacity=10, window_seconds=60)
        assert bucket.remaining == 10

    def test_consume_success(self):
        bucket = TokenBucket(capacity=5, window_seconds=60)
        assert bucket.consume() is True
        assert bucket.remaining == 4

    def test_consume_multiple(self):
        bucket = TokenBucket(capacity=3, window_seconds=60)
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.remaining == 0

    def test_consume_exhausted(self):
        bucket = TokenBucket(capacity=1, window_seconds=60)
        assert bucket.consume() is True
        assert bucket.consume() is False

    def test_consume_n(self):
        bucket = TokenBucket(capacity=5, window_seconds=60)
        assert bucket.consume(3) is True
        assert bucket.remaining == 2

    def test_consume_n_insufficient(self):
        bucket = TokenBucket(capacity=2, window_seconds=60)
        assert bucket.consume(3) is False

    def test_retry_after_when_available(self):
        bucket = TokenBucket(capacity=5, window_seconds=60)
        assert bucket.retry_after_seconds == 0

    def test_retry_after_when_exhausted(self):
        bucket = TokenBucket(capacity=1, window_seconds=60)
        bucket.consume()
        assert bucket.retry_after_seconds > 0

    def test_refill_over_time(self):
        bucket = TokenBucket(capacity=10, window_seconds=10)
        # Consume all
        for _ in range(10):
            bucket.consume()
        assert bucket.remaining == 0

        # Simulate time passing
        bucket._last_refill -= 5  # 5 seconds = 50% refill
        assert bucket.remaining >= 4  # at least 4-5 tokens refilled

    def test_refill_caps_at_capacity(self):
        bucket = TokenBucket(capacity=5, window_seconds=10)
        # Simulate lots of time
        bucket._last_refill -= 100
        assert bucket.remaining == 5

    def test_default_values(self):
        bucket = TokenBucket()
        assert bucket.capacity == 60
        assert bucket.window_seconds == 3600

    def test_remaining_returns_int(self):
        bucket = TokenBucket(capacity=5, window_seconds=60)
        assert isinstance(bucket.remaining, int)

    def test_retry_after_returns_int(self):
        bucket = TokenBucket(capacity=1, window_seconds=60)
        bucket.consume()
        assert isinstance(bucket.retry_after_seconds, int)

    def test_concurrent_consume_pattern(self):
        """Simulate rapid successive consumes."""
        bucket = TokenBucket(capacity=100, window_seconds=3600)
        successes = sum(1 for _ in range(100) if bucket.consume())
        assert successes == 100
        assert bucket.consume() is False

    def test_partial_refill(self):
        bucket = TokenBucket(capacity=60, window_seconds=3600)
        # Consume one
        bucket.consume()
        assert bucket.remaining == 59
        # Simulate 60 seconds passing → 1 token refilled (60/3600 * 60 = 1)
        bucket._last_refill -= 60
        assert bucket.remaining == 60  # back to full
