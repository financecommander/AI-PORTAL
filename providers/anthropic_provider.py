"""Anthropic provider implementation for FinanceCommander AI Portal."""

import os
from typing import List

import anthropic
from anthropic import AsyncAnthropic

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse


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
        import time
        start_time = time.time()

        try:
            # Convert messages to Anthropic format
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

            response = await self.client.messages.create(
                model=model,
                system=system_content,
                messages=anthropic_messages,
                max_tokens=kwargs.pop("max_tokens", 4096),
                **kwargs
            )

            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            latency_ms = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except anthropic.APIError as e:
            raise ProviderAPIError("anthropic", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("anthropic", 500, str(e)) from e

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available Anthropic models."""
        return [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku"
        ]