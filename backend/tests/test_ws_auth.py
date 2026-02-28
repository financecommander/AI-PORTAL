"""Tests for WebSocket first-message authentication (Bugs #1, #2)."""

import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.auth.jwt_handler import create_access_token


def test_ws_auth_valid_token(client: TestClient):
    """WebSocket connects successfully with valid JWT in first message."""
    token = create_access_token({"sub": "test-user", "domain": "test.com"})
    with client.websocket_connect("/api/v2/pipelines/ws/test-pipeline-1") as ws:
        # Send auth as first message
        ws.send_text(json.dumps({"type": "auth", "token": token}))
        # Send ping to verify connection is alive
        ws.send_text("ping")
        response = ws.receive_text()
        assert response == "pong"


def test_ws_auth_invalid_token(client: TestClient):
    """WebSocket closes with 1008 when JWT is invalid."""
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v2/pipelines/ws/test-pipeline-2") as ws:
            ws.send_text(json.dumps({"type": "auth", "token": "invalid.jwt.token"}))
            # Should receive close frame — trying to read will raise
            ws.receive_text()


def test_ws_auth_missing_token(client: TestClient):
    """WebSocket closes when first message has no token field."""
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v2/pipelines/ws/test-pipeline-3") as ws:
            ws.send_text(json.dumps({"type": "auth"}))
            ws.receive_text()


def test_ws_auth_wrong_message_type(client: TestClient):
    """WebSocket closes when first message type is not 'auth'."""
    token = create_access_token({"sub": "test-user"})
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v2/pipelines/ws/test-pipeline-4") as ws:
            ws.send_text(json.dumps({"type": "data", "token": token}))
            ws.receive_text()


def test_ws_auth_malformed_json(client: TestClient):
    """WebSocket closes when first message is not valid JSON."""
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v2/pipelines/ws/test-pipeline-5") as ws:
            ws.send_text("not json at all")
            ws.receive_text()


def test_ws_no_token_in_url(client: TestClient):
    """Verify token is NOT accepted as a query parameter (Bug #2)."""
    token = create_access_token({"sub": "test-user"})
    # Even with token in URL, should still require first-message auth
    with pytest.raises(Exception):
        with client.websocket_connect(
            f"/api/v2/pipelines/ws/test-pipeline-6?token={token}"
        ) as ws:
            # Don't send auth message — just try to ping
            ws.send_text("ping")
            ws.receive_text()


@pytest.mark.asyncio
async def test_ws_manager_connect_accepted():
    """connect_accepted registers WebSocket without calling accept()."""
    from backend.websockets.ws_manager import WebSocketManager

    manager = WebSocketManager()
    ws_mock = AsyncMock()

    await manager.connect_accepted("pipe-1", ws_mock)
    assert manager.get_connection_count("pipe-1") == 1
    # accept() should NOT be called — the route handler already accepted
    ws_mock.accept.assert_not_called()


@pytest.mark.asyncio
async def test_ws_manager_connect_calls_accept():
    """connect() (legacy) still calls accept() then registers."""
    from backend.websockets.ws_manager import WebSocketManager

    manager = WebSocketManager()
    ws_mock = AsyncMock()

    await manager.connect("pipe-2", ws_mock)
    assert manager.get_connection_count("pipe-2") == 1
    ws_mock.accept.assert_called_once()
