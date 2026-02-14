"""Live API tests – require real provider API keys.

Run with: python -m pytest tests/live/ -v -m live

These tests are skipped by default unless the corresponding
environment variable is set.
"""

from __future__ import annotations

import asyncio
import os

import pytest

from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.google_provider import GoogleProvider


pytestmark = pytest.mark.live


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
class TestOpenAILive:
    def test_simple_completion(self):
        provider = OpenAIProvider()
        response = asyncio.run(
            provider.send_message(
                messages=[{"role": "user", "content": "Say hello in one word."}],
                model="gpt-4o-mini",
                system_prompt="You are concise.",
                max_tokens=10,
            )
        )
        assert len(response.content) > 0
        assert response.input_tokens > 0


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
class TestAnthropicLive:
    def test_simple_completion(self):
        provider = AnthropicProvider()
        response = asyncio.run(
            provider.send_message(
                messages=[{"role": "user", "content": "Say hello in one word."}],
                model="claude-3-haiku",
                system_prompt="You are concise.",
                max_tokens=10,
            )
        )
        assert len(response.content) > 0


@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="GOOGLE_API_KEY not set")
class TestGoogleLive:
    def test_simple_completion(self):
        provider = GoogleProvider()
        response = asyncio.run(
            provider.send_message(
                messages=[{"role": "user", "content": "Say hello in one word."}],
                model="gemini-1.5-flash",
                system_prompt="You are concise.",
            )
        )
        assert len(response.content) > 0
