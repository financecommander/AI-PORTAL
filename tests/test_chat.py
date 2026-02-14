"""Tests for the chat engine and logger modules."""

import csv
import hashlib
from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest

from chat.engine import ChatEngine, Message
from chat.logger import UsageLogger, _hash_email
from config.pricing import estimate_cost
from providers.base import BaseProvider, ProviderResponse, StreamChunk
from specialists.manager import Specialist


# -- helpers --


class FakeProvider(BaseProvider):
    """A stub provider that returns canned responses."""

    def __init__(self, content="Hello from AI", model="gpt-4o"):
        self._content = content
        self._model = model

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        return ProviderResponse(
            content=self._content,
            model=self._model,
            input_tokens=10,
            output_tokens=20,
            latency_ms=100.0,
        )

    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        words = self._content.split()
        for word in words:
            yield StreamChunk(
                content=word + " ",
                is_final=False,
                input_tokens=0,
                output_tokens=0,
                model=self._model,
                latency_ms=0.0,
            )
        yield StreamChunk(
            content="",
            is_final=True,
            input_tokens=10,
            output_tokens=20,
            model=self._model,
            latency_ms=100.0,
        )

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def get_available_models(self) -> list[str]:
        return [self._model]


class FailingProvider(BaseProvider):
    """A provider that always raises an exception."""

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        raise RuntimeError("provider error")

    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        raise RuntimeError("stream error")
        yield  # pragma: no cover

    def count_tokens(self, text: str) -> int:
        return 0

    def get_available_models(self) -> list[str]:
        return []


@pytest.fixture
def specialist():
    return Specialist(
        id="test-spec",
        name="Test",
        system_prompt="You are a test bot.",
        model="gpt-4o",
        temperature=0.5,
    )


@pytest.fixture
def provider():
    return FakeProvider()


# -- ChatEngine tests --


class TestChatEngine:
    @pytest.mark.asyncio
    async def test_send_returns_content(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        reply = await engine.send("Hi")
        assert reply == "Hello from AI"

    def test_history_includes_system_prompt(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_history_grows_after_send(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        await engine.send("Hi")
        history = engine.get_history()
        # system + user + assistant
        assert len(history) == 3
        assert history[1]["role"] == "user"
        assert history[2]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_reset_clears_history(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        await engine.send("Hi")
        engine.reset()
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_set_specialist(self, provider, specialist):
        engine = ChatEngine(provider=provider)
        await engine.send("Hi")
        assert len(engine.get_history()) == 2  # user + assistant

        new_spec = Specialist(
            id="other", system_prompt="New prompt"
        )
        engine.set_specialist(new_spec)
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["content"] == "New prompt"

    @pytest.mark.asyncio
    async def test_no_specialist(self, provider):
        engine = ChatEngine(provider=provider)
        reply = await engine.send("Hi")
        assert reply == "Hello from AI"
        assert len(engine.get_history()) == 2

    @pytest.mark.asyncio
    async def test_logger_called_on_send(self, provider, specialist):
        logger = MagicMock(spec=UsageLogger)
        engine = ChatEngine(
            provider=provider,
            specialist=specialist,
            logger=logger,
            user_email="test@example.com",
        )
        await engine.send("Hi")
        logger.log.assert_called_once()
        call_kwargs = logger.log.call_args[1]
        assert call_kwargs["user_email"] == "test@example.com"
        assert call_kwargs["specialist_id"] == "test-spec"
        assert call_kwargs["specialist_name"] == "Test"
        assert call_kwargs["provider"] == "openai"
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["input_tokens"] == 10
        assert call_kwargs["output_tokens"] == 20
        assert call_kwargs["success"] is True
        assert isinstance(call_kwargs["latency_ms"], int)

    @pytest.mark.asyncio
    async def test_logger_called_on_failure(self, specialist):
        logger = MagicMock(spec=UsageLogger)
        engine = ChatEngine(
            provider=FailingProvider(),
            specialist=specialist,
            logger=logger,
            user_email="fail@example.com",
        )
        with pytest.raises(RuntimeError):
            await engine.send("Hi")

        logger.log.assert_called_once()
        call_kwargs = logger.log.call_args[1]
        assert call_kwargs["success"] is False
        assert call_kwargs["user_email"] == "fail@example.com"
        assert call_kwargs["provider"] == "openai"
        assert call_kwargs["input_tokens"] == 0
        assert call_kwargs["output_tokens"] == 0


# -- Email hashing tests --


class TestEmailHashing:
    def test_hash_email_returns_sha256(self):
        email = "User@Example.COM"
        expected = hashlib.sha256(
            "user@example.com".encode("utf-8")
        ).hexdigest()
        assert _hash_email(email) == expected

    def test_hash_email_strips_whitespace(self):
        assert _hash_email("  a@b.com  ") == _hash_email("a@b.com")

    def test_hash_email_deterministic(self):
        assert _hash_email("test@test.com") == _hash_email("test@test.com")


# -- UsageLogger tests --


class TestUsageLogger:
    def test_csv_header_matches_spec(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log(
            user_email="user@test.com",
            specialist_id="s1",
            specialist_name="General",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=200,
            latency_ms=150,
            success=True,
        )
        csv_files = list(tmp_path.glob("usage_*.csv"))
        assert len(csv_files) == 1
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == [
                "timestamp",
                "user_email_hash",
                "specialist_id",
                "specialist_name",
                "provider",
                "model",
                "input_tokens",
                "output_tokens",
                "estimated_cost_usd",
                "latency_ms",
                "success",
            ]

    def test_log_creates_csv(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log(
            user_email="user@test.com",
            specialist_id="s1",
            specialist_name="General",
            provider="openai",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=200,
            latency_ms=150,
            success=True,
        )
        csv_files = list(tmp_path.glob("usage_*.csv"))
        assert len(csv_files) == 1

    def test_log_appends_rows(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "General", "openai", "gpt-4o", 10, 20, 100, True)
        logger.log("c@d.com", "s2", "Analyst", "anthropic", "claude-3-sonnet", 30, 40, 200, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 2

    def test_log_includes_cost(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "General", "openai", "gpt-4o", 1000, 1000, 150, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        cost = float(rows[0]["estimated_cost_usd"])
        expected = estimate_cost("gpt-4o", 1000, 1000)
        assert abs(cost - expected) < 0.0001

    def test_log_hashes_email(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("user@test.com", "s1", "General", "openai", "gpt-4o", 10, 20, 100, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        # Should be a SHA-256 hex digest, not the raw email
        assert rows[0]["user_email_hash"] != "user@test.com"
        expected_hash = hashlib.sha256(
            "user@test.com".encode("utf-8")
        ).hexdigest()
        assert rows[0]["user_email_hash"] == expected_hash

    def test_log_records_provider(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "General", "anthropic", "claude-3-sonnet", 10, 20, 100, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]["provider"] == "anthropic"

    def test_log_records_specialist_name(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "Financial Analyst", "openai", "gpt-4o", 10, 20, 100, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]["specialist_name"] == "Financial Analyst"

    def test_log_records_latency(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "General", "openai", "gpt-4o", 10, 20, 250, True)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]["latency_ms"] == "250"

    def test_log_records_success(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "General", "openai", "gpt-4o", 10, 20, 100, True)
        logger.log("a@b.com", "s1", "General", "openai", "gpt-4o", 0, 0, 50, False)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[0]["success"] == "True"
        assert rows[1]["success"] == "False"


# -- Pricing tests --


class TestPricing:
    def test_known_model(self):
        cost = estimate_cost("gpt-4o", 1000, 1000)
        assert cost > 0

    def test_unknown_model(self):
        cost = estimate_cost("unknown-model", 1000, 1000)
        assert cost == 0.0

    def test_zero_tokens(self):
        cost = estimate_cost("gpt-4o", 0, 0)
        assert cost == 0.0
