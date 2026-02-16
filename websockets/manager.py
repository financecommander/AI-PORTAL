"""WebSocket connection manager for real-time pipeline streaming."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import WebSocket

from websockets.events import WSEvent


class ConnectionManager:
    """Manages WebSocket connections grouped by pipeline_id."""

    def __init__(self):
        self._connections: dict[str, list] = {}

    async def connect(self, pipeline_id: str, websocket) -> None:
        await websocket.accept()
        self._connections.setdefault(pipeline_id, []).append(websocket)

    async def disconnect(self, pipeline_id: str, websocket) -> None:
        conns = self._connections.get(pipeline_id, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(pipeline_id, None)

    async def send_event(self, pipeline_id: str, event: WSEvent) -> None:
        conns = self._connections.get(pipeline_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_text(event.to_json())
            except Exception:
                dead.append(ws)
        for ws in dead:
            conns.remove(ws)

    @property
    def active_connections(self) -> int:
        return sum(len(c) for c in self._connections.values())


ws_manager = ConnectionManager()
