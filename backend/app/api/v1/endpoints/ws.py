"""WebSocket endpoint for real-time dashboard state synchronization."""

import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.core.logging import logger
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager

router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_websocket_endpoint(websocket: WebSocket):
    """Real-time bidirectional WebSocket stream for dashboard clients."""
    await connection_manager.connect(websocket)

    # Send initial connection acknowledgment with current telemetry
    try:
        weather = await weather_service.get_current_weather()
        await connection_manager.send_personal_message(
            websocket,
            "connection_ack",
            {
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "weather": weather.to_dict(),
            },
        )
    except Exception as exc:
        logger.debug("Error sending initial WebSocket ack: %s", exc)

    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                msg = json.loads(raw_message)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await connection_manager.send_personal_message(
                        websocket,
                        "pong",
                        {"timestamp": datetime.now(timezone.utc).isoformat()},
                    )
                elif msg_type == "request_weather":
                    w = await weather_service.get_current_weather()
                    await connection_manager.send_personal_message(
                        websocket,
                        "weather_updated",
                        w.to_dict(),
                    )
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as exc:
        logger.debug("WebSocket client error: %s", exc)
        connection_manager.disconnect(websocket)
