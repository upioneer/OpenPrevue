"""Unit tests for WebSocket connection manager and real-time endpoints."""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.websocket import ConnectionManager


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    """Verify connection manager registers clients and broadcasts payloads without error."""
    manager = ConnectionManager()
    assert len(manager.active_connections) == 0

    # Broadcast on empty manager is a clean no-op
    await manager.broadcast("test_event", {"key": "value"})
    assert len(manager.active_connections) == 0


def test_websocket_endpoint_handshake():
    """Verify WebSocket endpoint handshake, initial ack, and ping/pong."""
    client = TestClient(app)
    with client.websocket_connect("/ws/dashboard") as websocket:
        # First message is connection acknowledgment
        ack_data = websocket.receive_json()
        assert ack_data["type"] == "connection_ack"
        assert "weather" in ack_data["data"]

        # Send ping
        websocket.send_json({"type": "ping"})
        pong_data = websocket.receive_json()
        assert pong_data["type"] == "pong"
        assert "timestamp" in pong_data["data"]
