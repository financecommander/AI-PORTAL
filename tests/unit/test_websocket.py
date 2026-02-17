"""Tests for WebSocket event types and connection manager."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from websockets.events import EventType, WSEvent
from websockets.manager import ConnectionManager


# ---------------------------------------------------------------------------
# EventType
# ---------------------------------------------------------------------------


class TestEventType:
    def test_values(self):
        assert EventType.PIPELINE_STARTED == "pipeline_started"
        assert EventType.AGENT_STARTED == "agent_started"
        assert EventType.AGENT_COMPLETED == "agent_completed"
        assert EventType.AGENT_FAILED == "agent_failed"
        assert EventType.PIPELINE_METRICS == "pipeline_metrics"
        assert EventType.PIPELINE_COMPLETED == "pipeline_completed"
        assert EventType.PIPELINE_FAILED == "pipeline_failed"
        assert EventType.ERROR == "error"

    def test_is_str_enum(self):
        assert isinstance(EventType.PIPELINE_STARTED, str)


# ---------------------------------------------------------------------------
# WSEvent
# ---------------------------------------------------------------------------


class TestWSEvent:
    def test_to_json(self):
        event = WSEvent(
            type=EventType.AGENT_STARTED,
            pipeline_id="pipe-123",
            data={"agent": "analyst", "model": "gpt-4o"},
        )
        parsed = json.loads(event.to_json())
        assert parsed["type"] == "agent_started"
        assert parsed["pipeline_id"] == "pipe-123"
        assert parsed["data"]["agent"] == "analyst"
        assert parsed["data"]["model"] == "gpt-4o"

    def test_to_json_empty_data(self):
        event = WSEvent(
            type=EventType.PIPELINE_STARTED,
            pipeline_id="pipe-456",
            data={},
        )
        parsed = json.loads(event.to_json())
        assert parsed["type"] == "pipeline_started"
        assert parsed["data"] == {}

    def test_to_json_error_event(self):
        event = WSEvent(
            type=EventType.ERROR,
            pipeline_id="pipe-789",
            data={"message": "Something went wrong"},
        )
        parsed = json.loads(event.to_json())
        assert parsed["type"] == "error"
        assert parsed["data"]["message"] == "Something went wrong"


# ---------------------------------------------------------------------------
# ConnectionManager
# ---------------------------------------------------------------------------


class TestConnectionManager:
    def test_initial_state(self):
        mgr = ConnectionManager()
        assert mgr.active_connections == 0

    @pytest.mark.asyncio
    async def test_connect(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect("pipe-1", ws)
        ws.accept.assert_awaited_once()
        assert mgr.active_connections == 1

    @pytest.mark.asyncio
    async def test_connect_multiple_to_same_pipeline(self):
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect("pipe-1", ws1)
        await mgr.connect("pipe-1", ws2)
        assert mgr.active_connections == 2

    @pytest.mark.asyncio
    async def test_connect_different_pipelines(self):
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect("pipe-1", ws1)
        await mgr.connect("pipe-2", ws2)
        assert mgr.active_connections == 2

    @pytest.mark.asyncio
    async def test_disconnect(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect("pipe-1", ws)
        assert mgr.active_connections == 1
        await mgr.disconnect("pipe-1", ws)
        assert mgr.active_connections == 0

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        # Should not raise
        await mgr.disconnect("pipe-1", ws)
        assert mgr.active_connections == 0

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_empty_pipeline(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect("pipe-1", ws)
        await mgr.disconnect("pipe-1", ws)
        assert "pipe-1" not in mgr._connections

    @pytest.mark.asyncio
    async def test_send_event(self):
        mgr = ConnectionManager()
        ws = AsyncMock()
        await mgr.connect("pipe-1", ws)

        event = WSEvent(
            type=EventType.AGENT_STARTED,
            pipeline_id="pipe-1",
            data={"agent": "test"},
        )
        await mgr.send_event("pipe-1", event)
        ws.send_text.assert_awaited_once_with(event.to_json())

    @pytest.mark.asyncio
    async def test_send_event_to_multiple_clients(self):
        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await mgr.connect("pipe-1", ws1)
        await mgr.connect("pipe-1", ws2)

        event = WSEvent(
            type=EventType.PIPELINE_COMPLETED,
            pipeline_id="pipe-1",
            data={"result": "done"},
        )
        await mgr.send_event("pipe-1", event)
        ws1.send_text.assert_awaited_once()
        ws2.send_text.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_event_removes_dead_connections(self):
        mgr = ConnectionManager()
        ws_alive = AsyncMock()
        ws_dead = AsyncMock()
        ws_dead.send_text.side_effect = Exception("connection closed")

        await mgr.connect("pipe-1", ws_alive)
        await mgr.connect("pipe-1", ws_dead)
        assert mgr.active_connections == 2

        event = WSEvent(
            type=EventType.AGENT_COMPLETED,
            pipeline_id="pipe-1",
            data={"agent": "test"},
        )
        await mgr.send_event("pipe-1", event)

        # Dead connection should be removed
        assert mgr.active_connections == 1

    @pytest.mark.asyncio
    async def test_send_event_no_connections(self):
        mgr = ConnectionManager()
        event = WSEvent(
            type=EventType.PIPELINE_STARTED,
            pipeline_id="pipe-none",
            data={},
        )
        # Should not raise
        await mgr.send_event("pipe-none", event)

    def test_ws_manager_singleton(self):
        from websockets.manager import ws_manager
        assert isinstance(ws_manager, ConnectionManager)
        assert ws_manager.active_connections == 0
