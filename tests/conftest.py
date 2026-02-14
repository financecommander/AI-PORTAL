"""Shared fixtures for all test categories.

Provides reusable fixtures for specialists, chat attachments, loggers,
and provider stubs.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest

from chat.file_handler import ChatAttachment
from providers.base import BaseProvider, ProviderResponse, StreamChunk
from specialists.manager import SpecialistManager


# ---------------------------------------------------------------------------
# Specialist fixtures
# ---------------------------------------------------------------------------

_SAMPLE_SPECIALISTS = {
    "specialists": [
        {
            "id": "fin_analyst",
            "name": "Financial Analyst",
            "description": "Crunches numbers",
            "provider": "openai",
            "model": "gpt-4o",
            "system_prompt": "You are a financial analyst.",
            "temperature": 0.3,
            "max_tokens": 4096,
            "pricing": {"input_per_1m": 2.50, "output_per_1m": 10.00},
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:00+00:00",
            "version": 1,
            "prompt_history": [],
        },
        {
            "id": "code_helper",
            "name": "Code Helper",
            "description": "Writes code",
            "provider": "anthropic",
            "model": "claude-3-sonnet",
            "system_prompt": "You are a coding assistant.",
            "temperature": 0.5,
            "max_tokens": 8192,
            "pricing": {"input_per_1m": 3.00, "output_per_1m": 15.00},
            "created_at": "2026-01-02T00:00:00+00:00",
            "updated_at": "2026-01-02T00:00:00+00:00",
            "version": 1,
            "prompt_history": [],
        },
    ]
}


@pytest.fixture
def specialists_file(tmp_path):
    """Write sample specialists JSON and return the path."""
    filepath = tmp_path / "specialists.json"
    filepath.write_text(json.dumps(_SAMPLE_SPECIALISTS))
    return str(filepath)


@pytest.fixture
def specialist_manager(specialists_file):
    """Provide a SpecialistManager loaded from the sample file."""
    return SpecialistManager(filepath=specialists_file)


# ---------------------------------------------------------------------------
# Chat attachment fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def text_attachment():
    """A simple text file attachment."""
    content = b"Hello, world!"
    return ChatAttachment(
        filename="hello.txt",
        content_type="text/plain",
        content_b64=base64.b64encode(content).decode(),
        size_bytes=len(content),
        text_content=content.decode(),
    )


@pytest.fixture
def image_attachment():
    """A PNG image attachment (fake bytes)."""
    content = b"\x89PNG fake image"
    return ChatAttachment(
        filename="chart.png",
        content_type="image/png",
        content_b64=base64.b64encode(content).decode(),
        size_bytes=len(content),
        text_content=None,
    )


@pytest.fixture
def pdf_attachment():
    """A PDF attachment (fake bytes)."""
    content = b"%PDF-1.4 fake content"
    return ChatAttachment(
        filename="report.pdf",
        content_type="application/pdf",
        content_b64=base64.b64encode(content).decode(),
        size_bytes=len(content),
        text_content="Extracted PDF text",
    )


# ---------------------------------------------------------------------------
# Logger fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def log_dir(tmp_path):
    """Provide a temporary directory for usage logs."""
    d = tmp_path / "logs"
    d.mkdir()
    return str(d)


# ---------------------------------------------------------------------------
# Provider stub fixtures
# ---------------------------------------------------------------------------


class StubProvider(BaseProvider):
    """Concrete BaseProvider subclass for testing.

    Returns canned responses without hitting any real API.
    """

    def __init__(self, response_text: str = "stub response", tokens: int = 10):
        self._response_text = response_text
        self._tokens = tokens

    async def send_message(self, messages, model, system_prompt, **kwargs):
        return ProviderResponse(
            content=self._response_text,
            input_tokens=self._tokens,
            output_tokens=self._tokens,
            model=model,
            latency_ms=1.0,
        )

    async def stream_message(self, messages, model, system_prompt, **kwargs):
        words = self._response_text.split()
        for i, word in enumerate(words):
            is_last = i == len(words) - 1
            yield StreamChunk(
                content=word + (" " if not is_last else ""),
                is_final=is_last,
                input_tokens=self._tokens if is_last else 0,
                output_tokens=self._tokens if is_last else 0,
                model=model,
                latency_ms=1.0 if is_last else 0.0,
            )

    def count_tokens(self, text):
        return len(text) // 4

    def get_available_models(self):
        return ["stub-model"]


@pytest.fixture
def stub_provider():
    """Provide a StubProvider instance."""
    return StubProvider()


@pytest.fixture
def chat_history():
    """Provide a sample chat history list."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
        {"role": "user", "content": "What is revenue?"},
        {"role": "assistant", "content": "Revenue is the total income generated."},
    ]
