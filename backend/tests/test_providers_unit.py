"""Test provider factory and base provider."""

import pytest
from backend.providers.factory import get_provider
from backend.providers.base import BaseProvider


def test_factory_returns_correct_provider():
    """Test factory returns correct provider class for each name."""
    # Note: These will use test keys from env
    openai = get_provider("openai")
    assert openai.name == "openai"

    anthropic = get_provider("anthropic")
    assert anthropic.name == "anthropic"

    google = get_provider("google")
    assert google.name == "google"

    xai = get_provider("xai")
    assert xai.name == "grok"  # As per factory


def test_factory_unknown_provider():
    """Test factory raises error for unknown provider."""
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("unknown")


def test_base_provider_abstract_methods():
    """Test base provider has abstract methods defined."""
    # This is more of a static check, but we can instantiate a subclass or check
    from backend.providers.openai_provider import OpenAIProvider
    provider = OpenAIProvider(api_key="test")
    assert hasattr(provider, "send_message")
    assert hasattr(provider, "stream_message")


# Note: Provider initialization assumed to work with config