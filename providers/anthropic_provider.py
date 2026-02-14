"""Anthropic provider implementation for FinanceCommander AI Portal."""

import os
import time
from collections.abc import AsyncGenerator
from typing import List

import anthropic
from anthropic import AsyncAnthropic

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse, StreamChunk


class AnthropicProvider(BaseProvider):
    """Anthropic API provider supporting Claude models."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")

        self.client = AsyncAnthropic(api_key=self.api_key)

    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        """Send message to Anthropic API."""
        start_time = time.perf_counter()

        try:
            anthropic_messages, system_content = self._convert_messages(
                messages, system_prompt
            )

            response = await self.client.messages.create(
                model=model,
                system=system_content,
                messages=anthropic_messages,
                max_tokens=kwargs.pop("max_tokens", 4096),
                **kwargs
            )

            content = response.content[0].text
            latency_ms = (time.perf_counter() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except anthropic.APIError as e:
            raise ProviderAPIError("anthropic", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("anthropic", 500, str(e)) from e

    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Yield response chunks as they arrive from Anthropic."""
        start = time.perf_counter()

        try:
            anthropic_messages, system_content = self._convert_messages(
                messages, system_prompt
            )

            async with self.client.messages.stream(
                model=model,
                system=system_content,
                messages=anthropic_messages,
                max_tokens=kwargs.pop("max_tokens", 4096),
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield StreamChunk(
                        content=text,
                        is_final=False,
                        input_tokens=0,
                        output_tokens=0,
                        model=model,
                        latency_ms=0,
                    )

                final = await stream.get_final_message()
                yield StreamChunk(
                    content="",
                    is_final=True,
                    input_tokens=final.usage.input_tokens,
                    output_tokens=final.usage.output_tokens,
                    model=model,
                    latency_ms=(time.perf_counter() - start) * 1000,
                )

        except anthropic.APIError as e:
            raise ProviderAPIError("anthropic", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("anthropic", 500, str(e)) from e

    def _convert_messages(
        self, messages: list[dict], system_prompt: str
    ) -> tuple[list[dict], str]:
        """Convert chat messages to Anthropic format, extracting system prompt."""
        anthropic_messages = []
        system_content = system_prompt

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        return anthropic_messages, system_content

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available Anthropic models."""
        return [
            "claude-opus-4-6",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ]