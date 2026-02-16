"""WebSocket connection manager for real-time event streaming."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts events to clients."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to add
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Broadcast an event to all connected clients.
        
        Automatically cleans up dead connections.
        
        Args:
            event_type: Type of event (e.g., 'progress', 'result')
            data: Event data to send
        """
        if not self.active_connections:
            logger.debug(f"No active connections to send event: {event_type}")
            return
        
        message = json.dumps({
            "type": event_type,
            "data": data,
        })
        
        # Track dead connections
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection)
    
    async def send_to(self, websocket: WebSocket, event_type: str, data: dict[str, Any]) -> None:
        """Send an event to a specific WebSocket connection.
        
        Args:
            websocket: Target WebSocket connection
            event_type: Type of event
            data: Event data to send
        """
        try:
            message = json.dumps({
                "type": event_type,
                "data": data,
            })
            await websocket.send_text(message)
        except Exception as e:
            logger.warning(f"Failed to send to specific WebSocket: {e}")
            self.disconnect(websocket)
    
    def count_connections(self) -> int:
        """Get the number of active connections.
        
        Returns:
            Number of active WebSocket connections
        """
        return len(self.active_connections)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
