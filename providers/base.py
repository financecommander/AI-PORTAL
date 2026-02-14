from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
<<<<<<< HEAD
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
=======
class ProviderResponse:
    """Standardized response from any LLM provider."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    latency_ms: float


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
    def count_tokens(self, text: str) -> int:
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        ...
>>>>>>> origin/main
