from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    latency_ms: float


@dataclass
class StreamChunk:
    """Single chunk from a streaming response."""
    content: str           # Text delta for this chunk
    is_final: bool         # True if this is the last chunk
    input_tokens: int      # Populated only on final chunk (0 otherwise)
    output_tokens: int     # Populated only on final chunk (0 otherwise)
    model: str
    latency_ms: float      # Total latency, populated only on final chunk


class BaseProvider(ABC):
    """Abstract base for all LLM provider integrations."""

    @abstractmethod
    async def send_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> ProviderResponse:
        ...

    @abstractmethod
    async def stream_message(
        self,
        messages: list[dict],
        model: str,
        system_prompt: str,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Yield response chunks as they arrive from the provider."""
        ...
        # Make this a generator (yield is required for AsyncGenerator typing)
        yield  # pragma: no cover

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        ...
