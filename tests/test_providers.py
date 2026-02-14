"""Tests for the provider base module."""

import pytest

from providers.base import BaseProvider, ProviderResponse


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

            def count_tokens(self, text: str) -> int:
                return 0

            def get_available_models(self) -> list[str]:
                return ["test-model"]

        provider = ValidProvider()
        # Test that it can be instantiated and has the required methods
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'count_tokens')
        assert hasattr(provider, 'get_available_models')
        # Test the methods work
        import asyncio
        result = asyncio.run(provider.send_message([], "test-model", ""))
        assert result.content == "ok"
        assert result.model == "test-model"
        assert provider.get_available_models() == ["test-model"]
