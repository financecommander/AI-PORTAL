"""Ollama provider — local/self-hosted models via OpenAI-compatible API.

Ollama exposes an OpenAI-compatible endpoint at /v1/chat/completions,
so we reuse AsyncOpenAI. All inference is free (cost_usd=0.0).
"""

import time
import httpx
from openai import AsyncOpenAI
from openai import (
    AuthenticationError as OpenAIAuthError,
    APITimeoutError as OpenAITimeoutError,
    APIError as OpenAIAPIError,
    APIConnectionError as OpenAIConnectionError,
)
from typing import AsyncGenerator

from backend.providers.base import BaseProvider, ProviderResponse, StreamChunk
from backend.config.settings import settings


class OllamaProvider(BaseProvider):
    def __init__(self):
        super().__init__("ollama")
        base_url = settings.ollama_base_url.rstrip("/")
        self.base_url = base_url
        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama doesn't require auth
            base_url=f"{base_url}/v1",
        )

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
        except OpenAIConnectionError:
            raise ConnectionError(f"Cannot reach Ollama at {self.base_url}. Is it running?")
        except OpenAITimeoutError:
            raise TimeoutError(f"Ollama request timed out ({self.base_url})")
        except OpenAIAPIError as e:
            raise RuntimeError(f"Ollama API error: {e}")

        latency = (time.perf_counter() - start) * 1000
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        return ProviderResponse(
            content=response.choices[0].message.content or "",
            model=response.model, input_tokens=input_tokens,
            output_tokens=output_tokens, latency_ms=latency,
            cost_usd=0.0,
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
        except OpenAIConnectionError:
            raise ConnectionError(f"Cannot reach Ollama at {self.base_url}. Is it running?")
        except OpenAITimeoutError:
            raise TimeoutError(f"Ollama request timed out ({self.base_url})")
        except OpenAIAPIError as e:
            raise RuntimeError(f"Ollama API error: {e}")

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
                    latency_ms=latency, cost_usd=0.0,
                )

    async def list_models(self) -> list[dict]:
        """Fetch available models from Ollama's native API."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [
                    {
                        "id": m["name"],
                        "name": m["name"],
                        "size": m.get("size", 0),
                        "modified_at": m.get("modified_at", ""),
                    }
                    for m in data.get("models", [])
                ]
        except Exception:
            return []

    async def is_healthy(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/version")
                return resp.status_code == 200
        except Exception:
            return False
