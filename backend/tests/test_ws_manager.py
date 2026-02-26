"""Tests for WebSocket manager."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from backend.websockets.ws_manager import WebSocketManager, WSEvent


@pytest.mark.asyncio
async def test_ws_event_to_json():
    """Test WSEvent serialization to JSON."""
    event = WSEvent(
        type="test_event",
        pipeline_id="test-123",
        timestamp="2024-01-01T00:00:00",
        data={"key": "value"}
    )
    
    json_str = event.to_json()
    assert "test_event" in json_str
    assert "test-123" in json_str
    assert "key" in json_str


@pytest.mark.asyncio
async def test_ws_manager_connect():
    """Test WebSocket connection registration."""
    manager = WebSocketManager()
    ws_mock = AsyncMock()
    
    await manager.connect("pipeline-1", ws_mock)
    
    assert manager.get_connection_count("pipeline-1") == 1
    ws_mock.accept.assert_called_once()


@pytest.mark.asyncio
async def test_ws_manager_disconnect():
    """Test WebSocket disconnection."""
    manager = WebSocketManager()
    ws_mock = AsyncMock()
    
    await manager.connect("pipeline-1", ws_mock)
    await manager.disconnect("pipeline-1", ws_mock)
    
    assert manager.get_connection_count("pipeline-1") == 0


@pytest.mark.asyncio
async def test_ws_manager_send_event():
    """Test sending event to WebSocket connections."""
    manager = WebSocketManager()
    ws_mock = AsyncMock()
    
    await manager.connect("pipeline-1", ws_mock)
    await manager.send_event("pipeline-1", "test_event", {"data": "value"})
    
    # Should have called send_text
    assert ws_mock.send_text.call_count == 1
