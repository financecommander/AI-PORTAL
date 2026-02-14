"""Tests for the chat engine streaming support."""

from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest

from chat.engine import ChatEngine, Message
from chat.logger import UsageLogger
from providers.base import BaseProvider, ProviderResponse, StreamChunk
from specialists.manager import Specialist


# -- helpers --


class FakeStreamProvider(BaseProvider):
    """Provider that yields a deterministic stream."""

    def __init__(self, chunks: list[str] | None = None, model: str = "gpt-4o"):
        self._chunks = chunks or ["Hello", " ", "world"]
        self._model = model

    async def send_message(
        self, messages, model, system_prompt, **kw
    ) -> ProviderResponse:
        content = "".join(self._chunks)
        return ProviderResponse(
            content=content, model=self._model,
            input_tokens=5, output_tokens=10, latency_ms=50.0,
        )

    async def stream_message(
        self, messages, model, system_prompt, **kw
    ) -> AsyncGenerator[StreamChunk, None]:
        for c in self._chunks:
            yield StreamChunk(
                content=c, is_final=False,
                input_tokens=0, output_tokens=0,
                model=self._model, latency_ms=0.0,
            )
        yield StreamChunk(
            content="", is_final=True,
            input_tokens=5, output_tokens=10,
            model=self._model, latency_ms=50.0,
        )

    def count_tokens(self, text):
        return len(text.split())

    def get_available_models(self):
        return [self._model]


class FailingStreamProvider(BaseProvider):
    """Provider whose stream_message raises."""

    async def send_message(self, messages, model, system_prompt, **kw):
        raise RuntimeError("send error")

    async def stream_message(self, messages, model, system_prompt, **kw):
        raise RuntimeError("stream error")
        yield  # pragma: no cover

    def count_tokens(self, text):
        return 0

    def get_available_models(self):
        return []


@pytest.fixture
def specialist():
    return Specialist(
        id="s1", name="Test", provider="openai",
        model="gpt-4o", system_prompt="Be helpful.",
    )


@pytest.fixture
def stream_provider():
    return FakeStreamProvider()


# -- Tests --


class TestStreamChunkDataclass:
    def test_content_chunk(self):
        chunk = StreamChunk(
            content="Hi", is_final=False,
            input_tokens=0, output_tokens=0,
            model="gpt-4o", latency_ms=0.0,
        )
        assert chunk.content == "Hi"
        assert chunk.is_final is False

    def test_final_chunk_has_usage(self):
        chunk = StreamChunk(
            content="", is_final=True,
            input_tokens=100, output_tokens=200,
            model="gpt-4o", latency_ms=300.0,
        )
        assert chunk.is_final is True
        assert chunk.input_tokens == 100
        assert chunk.output_tokens == 200
        assert chunk.latency_ms == 300.0


class TestSendStreaming:
    @pytest.mark.asyncio
    async def test_yields_content_chunks(self, stream_provider, specialist):
        engine = ChatEngine(provider=stream_provider, specialist=specialist)
        chunks = []
        async for chunk in engine.send_streaming("Hello"):
            chunks.append(chunk)
        content_chunks = [c for c in chunks if not c.is_final]
        assert len(content_chunks) == 3
        text = "".join(c.content for c in content_chunks)
        assert text == "Hello world"

    @pytest.mark.asyncio
    async def test_final_chunk_emitted(self, stream_provider, specialist):
        engine = ChatEngine(provider=stream_provider, specialist=specialist)
        chunks = []
        async for chunk in engine.send_streaming("Hello"):
            chunks.append(chunk)
        final = [c for c in chunks if c.is_final]
        assert len(final) == 1
        assert final[0].input_tokens == 5
        assert final[0].output_tokens == 10

    @pytest.mark.asyncio
    async def test_history_not_updated_by_streaming(self, stream_provider, specialist):
        """send_streaming should NOT auto-append assistant message."""
        engine = ChatEngine(provider=stream_provider, specialist=specialist)
        async for _ in engine.send_streaming("Hello"):
            pass
        # Should have system + user only
        assert len(engine.history) == 2
        assert engine.history[-1].role == "user"

    @pytest.mark.asyncio
    async def test_append_assistant_message(self, stream_provider, specialist):
        engine = ChatEngine(provider=stream_provider, specialist=specialist)
        full = ""
        async for chunk in engine.send_streaming("Hello"):
            if not chunk.is_final:
                full += chunk.content
        engine.append_assistant_message(full)
        assert engine.history[-1].role == "assistant"
        assert engine.history[-1].content == "Hello world"

    @pytest.mark.asyncio
    async def test_streaming_logs_on_final(self, stream_provider, specialist):
        logger = MagicMock(spec=UsageLogger)
        engine = ChatEngine(
            provider=stream_provider, specialist=specialist,
            logger=logger, user_email="a@b.com",
        )
        async for _ in engine.send_streaming("Hello"):
            pass
        logger.log.assert_called_once()
        kw = logger.log.call_args[1]
        assert kw["success"] is True
        assert kw["input_tokens"] == 5
        assert kw["output_tokens"] == 10

    @pytest.mark.asyncio
    async def test_streaming_failure_logs(self, specialist):
        logger = MagicMock(spec=UsageLogger)
        engine = ChatEngine(
            provider=FailingStreamProvider(), specialist=specialist,
            logger=logger,
        )
        with pytest.raises(RuntimeError):
            async for _ in engine.send_streaming("Hello"):
                pass
        logger.log.assert_called_once()
        kw = logger.log.call_args[1]
        assert kw["success"] is False

    @pytest.mark.asyncio
    async def test_empty_stream(self, specialist):
        """Provider that yields only a final chunk (no content)."""

        class EmptyStreamProvider(BaseProvider):
            async def send_message(self, messages, model, system_prompt, **kw):
                return ProviderResponse(
                    content="", model="gpt-4o",
                    input_tokens=0, output_tokens=0, latency_ms=0.0,
                )

            async def stream_message(self, messages, model, system_prompt, **kw):
                yield StreamChunk(
                    content="", is_final=True,
                    input_tokens=0, output_tokens=0,
                    model="gpt-4o", latency_ms=0.0,
                )

            def count_tokens(self, text):
                return 0

            def get_available_models(self):
                return ["gpt-4o"]

        engine = ChatEngine(provider=EmptyStreamProvider(), specialist=specialist)
        chunks = []
        async for chunk in engine.send_streaming("Hello"):
            chunks.append(chunk)
        assert len(chunks) == 1  # final only
        assert chunks[0].is_final is True

    @pytest.mark.asyncio
    async def test_multiple_sends_keep_history(self, stream_provider, specialist):
        engine = ChatEngine(provider=stream_provider, specialist=specialist)
        # First send
        full1 = ""
        async for chunk in engine.send_streaming("First"):
            if not chunk.is_final:
                full1 += chunk.content
        engine.append_assistant_message(full1)
        # Second send
        full2 = ""
        async for chunk in engine.send_streaming("Second"):
            if not chunk.is_final:
                full2 += chunk.content
        engine.append_assistant_message(full2)
        # system + user1 + asst1 + user2 + asst2
        assert len(engine.history) == 5
