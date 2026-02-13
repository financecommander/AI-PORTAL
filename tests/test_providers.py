"""Tests for the provider base module."""

import pytest

from providers.base import BaseProvider, ChatResponse


class TestChatResponse:
    def test_fields(self):
        resp = ChatResponse(
            content="Hello",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=20,
        )
        assert resp.content == "Hello"
        assert resp.model == "gpt-4o"
        assert resp.input_tokens == 10
        assert resp.output_tokens == 20


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
            def chat(self, messages, model, temperature=0.7, max_tokens=4096):
                return ChatResponse(
                    content="ok", model=model, input_tokens=0, output_tokens=0
                )

            def list_models(self):
                return ["test-model"]

        provider = ValidProvider()
        result = provider.chat([], "test-model")
        assert result.content == "ok"
        assert provider.list_models() == ["test-model"]
