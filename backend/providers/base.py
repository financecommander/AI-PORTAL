"""Abstract base for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator


@dataclass
class ProviderResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float = 0.0
    tool_calls: list[dict] | None = None


@dataclass
class StreamChunk:
    content: str
    is_final: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    latency_ms: float = 0.0
    cost_usd: float = 0.0


class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def send_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> ProviderResponse: ...

    async def stream_message(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        response = await self.send_message(
            messages=messages, model=model, temperature=temperature,
            max_tokens=max_tokens, system_prompt=system_prompt,
        )
        yield StreamChunk(
            content=response.content, is_final=True,
            input_tokens=response.input_tokens, output_tokens=response.output_tokens,
            model=response.model, latency_ms=response.latency_ms, cost_usd=response.cost_usd,
        )

    async def send_message_with_tools(
        self, messages: list[dict], model: str,
        temperature: float = 0.7, max_tokens: int = 4096,
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
    ) -> ProviderResponse:
        return await self.send_message(
            messages=messages, model=model, temperature=temperature,
            max_tokens=max_tokens, system_prompt=system_prompt,
        )
