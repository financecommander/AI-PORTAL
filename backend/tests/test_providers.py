"""
Tests for provider instantiation and responses.
"""
import pytest
from providers import OpenAIProvider, AnthropicProvider, GoogleProvider, ProviderResponse


class TestProviders:
    """Tests for provider instantiation."""
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider can be initialized."""
        provider = OpenAIProvider()
        assert provider is not None
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
    
    def test_anthropic_provider_initialization(self):
        """Test Anthropic provider can be initialized."""
        provider = AnthropicProvider()
        assert provider is not None
        assert hasattr(provider, 'send_message')
        assert hasattr(provider, 'stream_message')
    
    def test_google_provider_initialization(self):
        """Test Google provider can be initialized."""
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
            provider="openai",
            latency_ms=100
        )
        
        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
        assert response.model == "gpt-4o"
        assert response.provider == "openai"
        assert response.latency_ms == 100
