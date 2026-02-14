from .anthropic_provider import AnthropicProvider
from .base import BaseProvider, ProviderResponse
from .google_provider import GoogleProvider
from .openai_provider import OpenAIProvider

__all__ = [
    "BaseProvider",
    "ProviderResponse",
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleProvider",
    "get_provider"
]


def get_provider(name: str) -> BaseProvider:
    """Factory function to get provider instance by name."""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
    }

    provider_class = providers.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}")

    return provider_class()
