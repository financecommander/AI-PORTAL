"""Abstract base class for LLM provider integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatResponse:
    """Standardised response from any LLM provider."""

    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int


class BaseProvider(ABC):
    """Interface every provider must implement."""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        """Send messages and return a ChatResponse."""

    @abstractmethod
    def list_models(self) -> list[str]:
        """Return available model identifiers."""
