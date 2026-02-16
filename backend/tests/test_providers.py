"""
Tests for provider instantiation and responses.
"""
import pytest
import os
from providers import OpenAIProvider, AnthropicProvider, GoogleProvider, ProviderResponse


class TestProviders:
    """Tests for provider instantiation."""
    
    def test_openai_provider_initialization(self, monkeypatch):
        """Test OpenAI provider can be initialized."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        provider = OpenAIProvider()
        assert provider is not None
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
    
    def test_anthropic_provider_initialization(self, monkeypatch):
        """Test Anthropic provider can be initialized."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        provider = AnthropicProvider()
        assert provider is not None
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
    
    def test_google_provider_initialization(self, monkeypatch):
        """Test Google provider can be initialized."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        provider = GoogleProvider()
        assert provider is not None
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
    
    def test_provider_response_structure(self):
        """Test ProviderResponse structure."""
        response = ProviderResponse(
            content="Test response",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o",
            latency_ms=100
        )
        
        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.model == "gpt-4o"
        assert response.latency_ms == 100
