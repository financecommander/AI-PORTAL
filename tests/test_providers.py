"""Tests for the provider base module."""

import asyncio
from collections.abc import AsyncGenerator

import pytest

from providers.base import BaseProvider, ProviderResponse, StreamChunk


class TestProviderResponse:
    def test_fields(self):
        resp = ProviderResponse(
            content="Hello",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=20,
            latency_ms=100.0,
        )
        assert resp.content == "Hello"
        assert resp.model == "gpt-4o"
        assert resp.input_tokens == 10
        assert resp.output_tokens == 20
        assert resp.latency_ms == 100.0


class TestStreamChunk:
    def test_fields(self):
        chunk = StreamChunk(
            content="Hello",
            is_final=False,
            input_tokens=0,
            output_tokens=0,
            model="gpt-4o",
            latency_ms=0.0,
        )
        assert chunk.content == "Hello"
        assert chunk.is_final is False
        assert chunk.input_tokens == 0

    def test_final_chunk(self):
        chunk = StreamChunk(
            content="",
            is_final=True,
            input_tokens=100,
            output_tokens=200,
            model="gpt-4o",
            latency_ms=150.0,
        )
        assert chunk.is_final is True
        assert chunk.input_tokens == 100
        assert chunk.output_tokens == 200
        assert chunk.latency_ms == 150.0


class TestBaseProvider:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseProvider()

    def test_subclass_must_implement(self):
        class IncompleteProvider(BaseProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_valid_subclass(self):
        class ValidProvider(BaseProvider):
            async def send_message(
                self,
                messages: list[dict],
                model: str,
                system_prompt: str,
                **kwargs
            ) -> ProviderResponse:
                return ProviderResponse(
                    content="ok",
                    model=model,
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=0.0,
                )

            async def stream_message(
                self,
                messages: list[dict],
                model: str,
                system_prompt: str,
                **kwargs
            ) -> AsyncGenerator[StreamChunk, None]:
                yield StreamChunk(
                    content="ok",
                    is_final=True,
                    input_tokens=0,
                    output_tokens=0,
                    model=model,
                    latency_ms=0.0,
                )

            def count_tokens(self, text: str) -> int:
                return 0

            def get_available_models(self) -> list[str]:
                return ["test-model"]

        provider = ValidProvider()
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
        assert hasattr(provider, 'count_tokens')
        assert hasattr(provider, 'get_available_models')
        result = asyncio.run(provider.send_message([], "test-model", ""))
        assert result.content == "ok"
        assert result.model == "test-model"
        assert provider.get_available_models() == ["test-model"]
