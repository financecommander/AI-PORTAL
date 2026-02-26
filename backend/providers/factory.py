"""Provider factory. Single entry point for creating provider instances."""

from backend.config.settings import settings
from backend.providers.base import BaseProvider
from backend.providers.openai_provider import OpenAIProvider
from backend.providers.anthropic_provider import AnthropicProvider
from backend.providers.google_provider import GoogleProvider


def get_provider(provider_name: str) -> BaseProvider:
    match provider_name.lower():
        case "openai":
            return OpenAIProvider(api_key=settings.openai_api_key)
        case "grok" | "xai":
            return OpenAIProvider(
                api_key=settings.xai_api_key,
                base_url="https://api.x.ai/v1", name="grok",
            )
        case "anthropic":
            return AnthropicProvider(api_key=settings.anthropic_api_key)
        case "google" | "gemini":
            return GoogleProvider(api_key=settings.google_api_key)
        case _:
            raise ValueError(f"Unknown provider: '{provider_name}'. Available: openai, anthropic, google, grok")
