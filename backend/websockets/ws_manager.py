"""WebSocket connection manager for real-time pipeline updates."""

import asyncio
import json
from typing import Dict, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from fastapi import WebSocket


@dataclass
class WSEvent:
    """WebSocket event for pipeline progress."""
    type: str  # agent_start, agent_complete, token_update, error, complete
    pipeline_id: str
    timestamp: str
    data: dict

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(asdict(self))


class WebSocketManager:
    """Manages WebSocket connections for pipeline streaming."""

    def __init__(self):
        # pipeline_id -> set of connected WebSocket clients
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, pipeline_id: str, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection for a pipeline.

        Args:
            pipeline_id: Pipeline execution identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        await self.connect_accepted(pipeline_id, websocket)

    async def connect_accepted(self, pipeline_id: str, websocket: WebSocket):
        """Register an already-accepted WebSocket connection for a pipeline."""
        async with self._lock:
            if pipeline_id not in self._connections:
                self._connections[pipeline_id] = set()
            self._connections[pipeline_id].add(websocket)

    async def disconnect(self, pipeline_id: str, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            pipeline_id: Pipeline execution identifier
            websocket: WebSocket connection
        """
        async with self._lock:
            if pipeline_id in self._connections:
                self._connections[pipeline_id].discard(websocket)
                if not self._connections[pipeline_id]:
                    del self._connections[pipeline_id]

    async def broadcast(self, event: WSEvent):
        """
        Broadcast an event to all connections for a pipeline.
        
        Args:
            event: Event to broadcast
        """
        pipeline_id = event.pipeline_id
        async with self._lock:
            if pipeline_id not in self._connections:
                return
            
            # Create a copy to avoid modification during iteration
            connections = list(self._connections[pipeline_id])
        
        # Send to all connections outside the lock
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_text(event.to_json())
            except Exception:
                # Mark for removal if send fails
                disconnected.append(websocket)
        
        # Clean up failed connections
        if disconnected:
            async with self._lock:
                if pipeline_id in self._connections:
                    for ws in disconnected:
                        self._connections[pipeline_id].discard(ws)
                    if not self._connections[pipeline_id]:
                        del self._connections[pipeline_id]

    async def send_event(
        self,
        pipeline_id: str,
        event_type: str,
        data: dict
    ):
        """
        Send an event to all connections for a pipeline.
        
        Args:
            pipeline_id: Pipeline execution identifier
            event_type: Type of event
            data: Event data
        """
        event = WSEvent(
            type=event_type,
            pipeline_id=pipeline_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=data
        )
        await self.broadcast(event)

    def get_connection_count(self, pipeline_id: str) -> int:
        """Get number of active connections for a pipeline."""
        return len(self._connections.get(pipeline_id, set()))


# Global singleton instance
ws_manager = WebSocketManager()
