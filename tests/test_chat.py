"""Tests for the chat engine and logger modules."""

import csv
import os
from unittest.mock import MagicMock

import pytest

from chat.engine import ChatEngine, Message
from chat.logger import UsageLogger
from config.pricing import estimate_cost
from providers.base import BaseProvider, ChatResponse
from specialists.manager import Specialist


# -- helpers --


class FakeProvider(BaseProvider):
    """A stub provider that returns canned responses."""

    def __init__(self, content="Hello from AI", model="gpt-4o"):
        self._content = content
        self._model = model

    def chat(self, messages, model, temperature=0.7, max_tokens=4096):
        return ChatResponse(
            content=self._content,
            model=self._model,
            input_tokens=10,
            output_tokens=20,
        )

    def list_models(self):
        return [self._model]


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
    def test_send_returns_content(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        reply = engine.send("Hi")
        assert reply == "Hello from AI"

    def test_history_includes_system_prompt(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "system"

    def test_history_grows_after_send(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        engine.send("Hi")
        history = engine.get_history()
        # system + user + assistant
        assert len(history) == 3
        assert history[1]["role"] == "user"
        assert history[2]["role"] == "assistant"

    def test_reset_clears_history(self, provider, specialist):
        engine = ChatEngine(provider=provider, specialist=specialist)
        engine.send("Hi")
        engine.reset()
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "system"

    def test_set_specialist(self, provider, specialist):
        engine = ChatEngine(provider=provider)
        engine.send("Hi")
        assert len(engine.get_history()) == 2  # user + assistant

        new_spec = Specialist(
            id="other", system_prompt="New prompt"
        )
        engine.set_specialist(new_spec)
        history = engine.get_history()
        assert len(history) == 1
        assert history[0]["content"] == "New prompt"

    def test_no_specialist(self, provider):
        engine = ChatEngine(provider=provider)
        reply = engine.send("Hi")
        assert reply == "Hello from AI"
        assert len(engine.get_history()) == 2

    def test_logger_called_on_send(self, provider, specialist):
        logger = MagicMock(spec=UsageLogger)
        engine = ChatEngine(
            provider=provider,
            specialist=specialist,
            logger=logger,
            user_email="test@example.com",
        )
        engine.send("Hi")
        logger.log.assert_called_once_with(
            user_email="test@example.com",
            specialist_id="test-spec",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=20,
        )


# -- UsageLogger tests --


class TestUsageLogger:
    def test_log_creates_csv(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log(
            user_email="user@test.com",
            specialist_id="s1",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=200,
        )
        csv_files = list(tmp_path.glob("usage_*.csv"))
        assert len(csv_files) == 1

    def test_log_appends_rows(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "gpt-4o", 10, 20)
        logger.log("c@d.com", "s2", "gpt-4o", 30, 40)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 2

    def test_log_includes_cost(self, tmp_path):
        logger = UsageLogger(log_dir=str(tmp_path))
        logger.log("a@b.com", "s1", "gpt-4o", 1000, 1000)
        csv_files = list(tmp_path.glob("usage_*.csv"))
        with open(csv_files[0], newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        cost = float(rows[0]["estimated_cost"])
        expected = estimate_cost("gpt-4o", 1000, 1000)
        assert abs(cost - expected) < 0.0001


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
