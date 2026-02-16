"""Tests for WebSocket connection manager.

Tests WebSocket connection management, event broadcasting, and cleanup.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.websockets.manager import WebSocketManager


@pytest.fixture
def ws_manager():
    """Provide a fresh WebSocketManager instance for each test."""
    return WebSocketManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    return ws


class TestWebSocketManager:
    """Tests for WebSocketManager class."""
    
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, ws_manager, mock_websocket):
        """Test connecting and disconnecting a WebSocket client."""
        # Initially no connections
        assert ws_manager.count_connections() == 0
        
        # Connect
        await ws_manager.connect(mock_websocket)
        assert ws_manager.count_connections() == 1
        assert mock_websocket.accept.called
        
        # Disconnect
        ws_manager.disconnect(mock_websocket)
        assert ws_manager.count_connections() == 0
    
    @pytest.mark.asyncio
    async def test_send_event_to_connected_client(self, ws_manager, mock_websocket):
        """Test sending an event to a connected WebSocket client."""
        # Connect the client
        await ws_manager.connect(mock_websocket)
        
        # Send an event
        await ws_manager.send_event("test_event", {"message": "hello"})
        
        # Verify the message was sent
        assert mock_websocket.send_text.called
        call_args = mock_websocket.send_text.call_args[0][0]
        assert "test_event" in call_args
        assert "hello" in call_args
    
    @pytest.mark.asyncio
    async def test_send_event_with_no_connections(self, ws_manager):
        """Test sending event when no connections exist doesn't crash."""
        # Should not raise an exception
        await ws_manager.send_event("test", {"data": "value"})
        assert ws_manager.count_connections() == 0
    
    @pytest.mark.asyncio
    async def test_dead_connections_cleaned_up(self, ws_manager):
        """Test that dead connections are automatically removed during broadcast."""
        # Create a mock WebSocket that will fail on send
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock(side_effect=Exception("Connection closed"))
        
        # Connect the client
        await ws_manager.connect(mock_ws)
        assert ws_manager.count_connections() == 1
        
        # Try to send an event - should clean up the dead connection
        await ws_manager.send_event("test", {"message": "test"})
        
        # Dead connection should be removed
        assert ws_manager.count_connections() == 0
