"""WebSocket connection manager and real-time state broadcaster."""

import json
from fastapi import WebSocket
from backend.app.core.logging import logger


class ConnectionManager:
    """Manages active dashboard WebSocket client connections and event broadcasting."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept incoming client connection and register in active pool."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Dashboard WebSocket client connected. Total active clients: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove disconnected client from active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("Dashboard WebSocket client disconnected. Total active clients: %d", len(self.active_connections))

    async def broadcast(self, event_type: str, data: dict | list) -> None:
        """Broadcast structured JSON event to all connected dashboard displays."""
        if not self.active_connections:
            return

        payload = json.dumps({"type": event_type, "data": data})
        disconnected: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as exc:
                logger.debug("Failed sending WebSocket message to client: %s", exc)
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message(self, websocket: WebSocket, event_type: str, data: dict | list) -> None:
        """Send a direct JSON message to a single specific client."""
        payload = json.dumps({"type": event_type, "data": data})
        try:
            await websocket.send_text(payload)
        except Exception as exc:
            logger.debug("Failed sending direct WebSocket message: %s", exc)
            self.disconnect(websocket)


connection_manager = ConnectionManager()
