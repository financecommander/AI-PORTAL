"""OpenAI and Grok (xAI) provider. Grok uses same API with different base_url."""

import time
from openai import AsyncOpenAI
from openai import (
    AuthenticationError as OpenAIAuthError,
    RateLimitError as OpenAIRateLimitError,
    APITimeoutError as OpenAITimeoutError,
    APIError as OpenAIAPIError,
)
from typing import AsyncGenerator

from backend.providers.base import BaseProvider, ProviderResponse, StreamChunk
from backend.utils.token_estimator import calculate_cost
from backend.errors.exceptions import ProviderError, ProviderAuthError, ProviderRateLimitError, ProviderTimeoutError


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str | None = None, name: str = "openai"):
        super().__init__(name)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        start = time.perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=model, messages=full_messages,
                temperature=temperature, max_tokens=max_tokens,
            )
        except OpenAIAuthError:
            raise ProviderAuthError(self.name)
        except OpenAIRateLimitError as e:
            raise ProviderRateLimitError(self.name, getattr(e, "retry_after", None))
        except OpenAITimeoutError:
            raise ProviderTimeoutError(self.name, 60.0)
        except OpenAIAPIError as e:
            raise ProviderError(self.name, str(e))

        latency = (time.perf_counter() - start) * 1000
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        return ProviderResponse(
            content=response.choices[0].message.content or "",
            model=response.model, input_tokens=input_tokens,
            output_tokens=output_tokens, latency_ms=latency,
            cost_usd=calculate_cost(model, input_tokens, output_tokens),
        )

    async def stream_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        start = time.perf_counter()
        try:
            stream = await self.client.chat.completions.create(
                model=model, messages=full_messages,
                temperature=temperature, max_tokens=max_tokens,
                stream=True, stream_options={"include_usage": True},
            )
        except OpenAIAuthError:
            raise ProviderAuthError(self.name)
        except OpenAIRateLimitError as e:
            raise ProviderRateLimitError(self.name, getattr(e, "retry_after", None))
        except OpenAITimeoutError:
            raise ProviderTimeoutError(self.name, 60.0)
        except OpenAIAPIError as e:
            raise ProviderError(self.name, str(e))

        input_tokens = 0
        output_tokens = 0

        async for chunk in stream:
            if chunk.usage:
                input_tokens = chunk.usage.prompt_tokens or 0
                output_tokens = chunk.usage.completion_tokens or 0
            if chunk.choices and chunk.choices[0].delta.content:
                yield StreamChunk(content=chunk.choices[0].delta.content)
            if chunk.choices and chunk.choices[0].finish_reason:
                latency = (time.perf_counter() - start) * 1000
                yield StreamChunk(
                    content="", is_final=True, input_tokens=input_tokens,
                    output_tokens=output_tokens, model=model,
                    latency_ms=latency, cost_usd=calculate_cost(model, input_tokens, output_tokens),
                )
