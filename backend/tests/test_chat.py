"""Tests for chat endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from providers.base import ProviderResponse, StreamChunk


class TestChatEndpoints:
    """Test chat API endpoints."""

    @pytest.mark.asyncio
    async def test_send_chat_success(self, client, mock_specialist_manager):
        """Test successful non-streaming chat."""
        # Mock provider response
        mock_response = ProviderResponse(
            content="This is a test response.",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o",
            latency_ms=1000.0
        )
        
        with patch("backend.routes.chat.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.send_message = AsyncMock(return_value=mock_response)
            mock_get_provider.return_value = mock_provider
            
            response = client.post(
                "/chat/send",
                json={
                    "specialist_id": "test-specialist-id",
                    "message": "Hello, world!",
                    "conversation_history": []
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "This is a test response."
            assert data["specialist_id"] == "test-specialist-id"
            assert data["specialist_name"] == "Test Specialist"
            assert data["provider"] == "openai"
            assert data["model"] == "gpt-4o"
            assert data["input_tokens"] == 10
            assert data["output_tokens"] == 5
            assert "estimated_cost_usd" in data
            assert "latency_ms" in data

    def test_send_chat_invalid_specialist(self, client):
        """Test chat with invalid specialist ID."""
        response = client.post(
            "/chat/send",
            json={
                "specialist_id": "invalid-specialist-id",
                "message": "Hello!",
                "conversation_history": []
            }
        )
        
        assert response.status_code == 404
        assert "Specialist not found" in response.json()["detail"]

    def test_send_chat_with_history(self, client, mock_specialist_manager):
        """Test chat with conversation history."""
        mock_response = ProviderResponse(
            content="Response based on history.",
            input_tokens=20,
            output_tokens=10,
            model="gpt-4o",
            latency_ms=1200.0
        )
        
        with patch("backend.routes.chat.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.send_message = AsyncMock(return_value=mock_response)
            mock_get_provider.return_value = mock_provider
            
            response = client.post(
                "/chat/send",
                json={
                    "specialist_id": "test-specialist-id",
                    "message": "What did I ask before?",
                    "conversation_history": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi there!"}
                    ]
                }
            )
            
            assert response.status_code == 200
            
            # Verify send_message was called with history
            call_args = mock_provider.send_message.call_args
            messages = call_args.kwargs["messages"]
            assert len(messages) == 3  # 2 history + 1 new message
            assert messages[0]["content"] == "Hello"
            assert messages[1]["content"] == "Hi there!"
            assert messages[2]["content"] == "What did I ask before?"

    @pytest.mark.asyncio
    async def test_send_chat_provider_error(self, client, mock_specialist_manager):
        """Test handling of provider errors."""
        with patch("backend.routes.chat.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.send_message = AsyncMock(side_effect=Exception("API Error"))
            mock_get_provider.return_value = mock_provider
            
            response = client.post(
                "/chat/send",
                json={
                    "specialist_id": "test-specialist-id",
                    "message": "Hello!",
                    "conversation_history": []
                }
            )
            
            assert response.status_code == 500
            assert "Provider error" in response.json()["detail"]

    def test_send_chat_validates_request(self, client):
        """Test request validation."""
        # Missing required field
        response = client.post(
            "/chat/send",
            json={
                "specialist_id": "test-specialist-id"
                # Missing 'message' field
            }
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_send_chat_logs_usage(self, client, session, mock_specialist_manager):
        """Test that usage is logged to database."""
        mock_response = ProviderResponse(
            content="Test response",
            input_tokens=10,
            output_tokens=5,
            model="gpt-4o",
            latency_ms=1000.0
        )
        
        with patch("backend.routes.chat.get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.send_message = AsyncMock(return_value=mock_response)
            mock_get_provider.return_value = mock_provider
            
            response = client.post(
                "/chat/send",
                json={
                    "specialist_id": "test-specialist-id",
                    "message": "Hello!",
                    "conversation_history": []
                }
            )
            
            assert response.status_code == 200
            
            # Check that usage was logged
            from sqlmodel import select
            from backend.models.usage_log import UsageLog
            statement = select(UsageLog)
            logs = session.exec(statement).all()
            
            assert len(logs) == 1
            log = logs[0]
            assert log.specialist_id == "test-specialist-id"
            assert log.input_tokens == 10
            assert log.output_tokens == 5
            assert log.success is True

    def test_stream_chat_endpoint_exists(self, client):
        """Test that streaming endpoint exists."""
        # This will fail if specialist doesn't exist, but endpoint should be reachable
        response = client.post(
            "/chat/stream",
            json={
                "specialist_id": "invalid-id",
                "message": "Hello!",
                "conversation_history": []
            }
        )
        
        # Should get 404 for invalid specialist, not 404 for missing endpoint
        assert response.status_code == 404
        assert "Specialist not found" in response.json()["detail"]


class TestChatModels:
    """Test request/response models."""

    def test_chat_request_model(self):
        """Test ChatRequest model validation."""
        from backend.models.chat import ChatRequest
        
        request = ChatRequest(
            specialist_id="test-id",
            message="Hello!",
            conversation_history=[]
        )
        
        assert request.specialist_id == "test-id"
        assert request.message == "Hello!"
        assert request.conversation_history == []

    def test_chat_request_with_history(self):
        """Test ChatRequest with conversation history."""
        from backend.models.chat import ChatRequest, ChatMessage
        
        request = ChatRequest(
            specialist_id="test-id",
            message="What's next?",
            conversation_history=[
                ChatMessage(role="user", content="Hello"),
                ChatMessage(role="assistant", content="Hi!")
            ]
        )
        
        assert len(request.conversation_history) == 2
        assert request.conversation_history[0].role == "user"
        assert request.conversation_history[1].content == "Hi!"

    def test_chat_response_model(self):
        """Test ChatResponse model."""
        from backend.models.chat import ChatResponse
        
        response = ChatResponse(
            content="Test response",
            specialist_id="test-id",
            specialist_name="Test Specialist",
            provider="openai",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=5,
            estimated_cost_usd=0.001,
            latency_ms=1234.5
        )
        
        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 5
