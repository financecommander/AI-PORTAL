"""Llama provider implementation for FinanceCommander AI Portal."""

from __future__ import annotations

import os
import time
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, List

import openai
from openai import AsyncOpenAI

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse, StreamChunk

if TYPE_CHECKING:
    from chat.file_handler import ChatAttachment


class LlamaProvider(BaseProvider):
    """Llama API provider for self-hosted models."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or "dummy"  # Self-hosted, no real key needed
        self.base_url = base_url or os.getenv("LLAMA_BASE_URL") or os.getenv("LLAMA_VM_URL", "http://localhost:8000/v1")
        if not self.api_key:
            raise ValueError("Llama API key required")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        """Send message to Llama API."""
        start_time = time.perf_counter()

        try:
            full_messages = self._build_messages(messages, system_prompt)

            response = await self.client.chat.completions.create(
                model=model,
                messages=full_messages,
                **kwargs
            )

            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            latency_ms = (time.perf_counter() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except openai.APIError as e:
            raise ProviderAPIError("llama", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("llama", 500, str(e)) from e

    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Yield response chunks as they arrive from Llama."""
        start = time.perf_counter()

        try:
            full_messages = self._build_messages(messages, system_prompt)
            kwargs.pop("stream", None)

            stream = await self.client.chat.completions.create(
                model=model,
                messages=full_messages,
                stream=True,
                stream_options={"include_usage": True},
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield StreamChunk(
                        content=chunk.choices[0].delta.content,
                        is_final=False,
                        input_tokens=0,
                        output_tokens=0,
                        model=model,
                        latency_ms=0,
                    )

                if chunk.usage:
                    yield StreamChunk(
                        content="",
                        is_final=True,
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                        model=model,
                        latency_ms=(time.perf_counter() - start) * 1000,
                    )

        except openai.APIError as e:
            raise ProviderAPIError("llama", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("llama", 500, str(e)) from e

    def _build_messages(self, messages: list[dict], system_prompt: str) -> list[dict]:
        """Prepend system prompt if not already present."""
        if system_prompt and (not messages or messages[0].get("role") != "system"):
            return [{"role": "system", "content": system_prompt}] + messages
        return list(messages)

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available Llama models."""
        return [
            "llama-4-8b",
            "llama-4-70b",
            "llama-4-405b",
        ]

    def format_attachment(self, attachment: ChatAttachment) -> dict:
        """Format attachment for Llama API.

        Images are sent as ``image_url`` content blocks (base64 data URI).
        Text-based files have their content injected as a text block.
        """
        if attachment.content_type and attachment.content_type.startswith("image/"):
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{attachment.content_type};base64,{attachment.content_b64}",
                },
            }
        return super().format_attachment(attachment)