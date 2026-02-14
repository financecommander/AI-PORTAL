"""OpenAI provider implementation for FinanceCommander AI Portal."""

import os
from typing import List

import openai
from openai import AsyncOpenAI

from portal.errors import ProviderAPIError
from providers.base import BaseProvider, ProviderResponse


class OpenAIProvider(BaseProvider):
    """OpenAI API provider supporting GPT models."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_API_BASE")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

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
        """Send message to OpenAI API."""
        import time
        start_time = time.time()

        try:
            # Add system prompt if not already present
            if messages and messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": system_prompt})

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )

            content = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            latency_ms = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                latency_ms=latency_ms
            )

        except openai.APIError as e:
            raise ProviderAPIError("openai", e.status_code or 500, str(e)) from e
        except Exception as e:
            raise ProviderAPIError("openai", 500, str(e)) from e

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """Return list of available OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "grok-2"  # Via OpenAI-compatible API
        ]