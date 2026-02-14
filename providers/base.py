from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chat.file_handler import ChatAttachment


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

    def format_attachment(self, attachment: ChatAttachment) -> dict:
        """Convert a ChatAttachment into the provider's expected message format.

        The default implementation injects text_content into a user message.
        Subclasses should override for native image / document support.

        Args:
            attachment: Processed file attachment.

        Returns:
            A dict suitable for inclusion in the provider's message list,
            or a content block dict for providers that support multipart.
        """
        if attachment.text_content:
            return {
                "type": "text",
                "text": (
                    f"[Attached file: {attachment.filename}]\n\n"
                    f"{attachment.text_content}"
                ),
            }
        return {
            "type": "text",
            "text": f"[Attached file: {attachment.filename} ({attachment.size_bytes} bytes)]",
        }
