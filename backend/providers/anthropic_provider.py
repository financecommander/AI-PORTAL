"""Anthropic (Claude) provider."""

import time
from anthropic import AsyncAnthropic
from anthropic import (
    AuthenticationError as AnthropicAuthError,
    RateLimitError as AnthropicRateLimitError,
    APITimeoutError as AnthropicTimeoutError,
    APIError as AnthropicAPIError,
)
from typing import AsyncGenerator

from backend.providers.base import BaseProvider, ProviderResponse, StreamChunk
from backend.utils.token_estimator import calculate_cost
from backend.errors.exceptions import ProviderError, ProviderAuthError, ProviderRateLimitError, ProviderTimeoutError


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("anthropic")
        self.client = AsyncAnthropic(api_key=api_key)

    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        start = time.perf_counter()
        try:
            kwargs = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
            if system_prompt:
                kwargs["system"] = system_prompt
            response = await self.client.messages.create(**kwargs)
        except AnthropicAuthError:
            raise ProviderAuthError(self.name)
        except AnthropicRateLimitError:
            raise ProviderRateLimitError(self.name)
        except AnthropicTimeoutError:
            raise ProviderTimeoutError(self.name, 60.0)
        except AnthropicAPIError as e:
            raise ProviderError(self.name, str(e))

        latency = (time.perf_counter() - start) * 1000
        content = "".join(block.text for block in response.content if block.type == "text")

        return ProviderResponse(
            content=content, model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency,
            cost_usd=calculate_cost(model, response.usage.input_tokens, response.usage.output_tokens),
        )

    async def stream_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        start = time.perf_counter()
        try:
            kwargs = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
            if system_prompt:
                kwargs["system"] = system_prompt
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield StreamChunk(content=text)
                final = await stream.get_final_message()
                latency = (time.perf_counter() - start) * 1000
                yield StreamChunk(
                    content="", is_final=True,
                    input_tokens=final.usage.input_tokens,
                    output_tokens=final.usage.output_tokens,
                    model=final.model, latency_ms=latency,
                    cost_usd=calculate_cost(model, final.usage.input_tokens, final.usage.output_tokens),
                )
        except AnthropicAuthError:
            raise ProviderAuthError(self.name)
        except AnthropicRateLimitError:
            raise ProviderRateLimitError(self.name)
        except AnthropicTimeoutError:
            raise ProviderTimeoutError(self.name, 60.0)
        except AnthropicAPIError as e:
            raise ProviderError(self.name, str(e))
