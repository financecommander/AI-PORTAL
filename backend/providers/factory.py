"""Provider factory. Single entry point for creating provider instances."""

import os
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
        case "deepseek":
            return OpenAIProvider(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com", name="deepseek",
            )
        case "mistral":
            return OpenAIProvider(
                api_key=settings.mistral_api_key,
                base_url="https://api.mistral.ai/v1", name="mistral",
            )
        case "anthropic":
            return AnthropicProvider(api_key=settings.anthropic_api_key)
        case "google" | "gemini":
            return GoogleProvider(api_key=settings.google_api_key)
        case "local" | "ternary" | "local-ternary":
            from backend.providers.local_ternary_provider import LocalTernaryProvider
            # Prefer Triton checkpoint dir, fall back to generic path
            model_path = os.getenv(
                "TERNARY_MODEL_PATH",
                os.getenv("TRITON_CHECKPOINT_DIR", "checkpoints/credit_risk"),
            )
            return LocalTernaryProvider(model_path=model_path)
        case _:
            raise ValueError(f"Unknown provider: '{provider_name}'. Available: openai, anthropic, google, grok, deepseek, mistral, local")
