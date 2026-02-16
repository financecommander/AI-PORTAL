"""
Tests for provider factory and instantiation.
"""
import pytest
from providers import get_provider, OpenAIProvider, AnthropicProvider, GoogleProvider


class TestProviderFactory:
    """Tests for provider factory function."""
    
    def test_get_openai_provider(self, monkeypatch):
        """Test getting OpenAI provider."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)
    
    def test_get_openai_provider_with_base_url(self, monkeypatch):
        """Test getting OpenAI provider with custom base URL."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = get_provider("openai", base_url="https://custom.url")
        assert isinstance(provider, OpenAIProvider)
    
    def test_get_anthropic_provider(self, monkeypatch):
        """Test getting Anthropic provider."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        provider = get_provider("anthropic")
        assert isinstance(provider, AnthropicProvider)
    
    def test_get_google_provider(self, monkeypatch):
        """Test getting Google provider."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        provider = get_provider("google")
        assert isinstance(provider, GoogleProvider)
    
    def test_get_provider_case_insensitive(self, monkeypatch):
        """Test provider names are case insensitive."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = get_provider("OpenAI")
        assert isinstance(provider, OpenAIProvider)
    
    def test_get_invalid_provider(self):
        """Test getting invalid provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid-provider")
        
        assert "Unknown provider" in str(exc_info.value)
