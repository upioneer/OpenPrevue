"""Integrations router for Home Assistant, Kiosk display power, and smart home automation."""

import subprocess
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from backend.app.core.logging import logger
from backend.app.services.homeassistant import homeassistant_service
from backend.app.services.websocket import connection_manager

router = APIRouter(prefix="/integrations")


class DisplayPowerRequest(BaseModel):
    """Payload to command physical kiosk display or broadcast screen sleep."""
    state: str  # "on", "off", "toggle"


@router.get("/homeassistant/sensors")
async def get_homeassistant_sensors() -> dict:
    """Provide structured JSON state and attributes for Home Assistant REST integration."""
    return await homeassistant_service.get_sensor_payload()


@router.get("/homeassistant/yaml-config")
async def get_homeassistant_yaml(request: Request) -> dict:
    """Generate ready-to-paste Home Assistant YAML snippet with auto-detected host."""
    base_url = str(request.base_url).rstrip("/")
    yaml_text = homeassistant_service.generate_yaml_configuration(base_url)
    return {
        "status": "success",
        "base_url": base_url,
        "yaml": yaml_text,
    }


@router.post("/display/power")
async def set_display_power(payload: DisplayPowerRequest) -> dict:
    """Toggle physical display power (via CEC / vcgencmd) and broadcast WebSocket screen state."""
    state = payload.state.lower().strip()
    if state not in ("on", "off", "toggle"):
        raise HTTPException(status_code=400, detail="State must be 'on', 'off', or 'toggle'")

    executed_cmd = None
    cmd_success = False

    # 1. Attempt Raspberry Pi / Linux CEC / vcgencmd execution if available
    try:
        if state == "on":
            # Try cec-client or vcgencmd
            proc = subprocess.run(
                ["which", "vcgencmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1.0,
            )
            if proc.returncode == 0:
                subprocess.run(["vcgencmd", "display_power", "1"], timeout=2.0)
                executed_cmd = "vcgencmd display_power 1"
                cmd_success = True
        elif state == "off":
            proc = subprocess.run(
                ["which", "vcgencmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1.0,
            )
            if proc.returncode == 0:
                subprocess.run(["vcgencmd", "display_power", "0"], timeout=2.0)
                executed_cmd = "vcgencmd display_power 0"
                cmd_success = True
    except Exception as exc:
        logger.debug("Physical display power command skipped: %s", exc)

    # 2. Broadcast display power state via WebSocket to all connected browser displays
    await connection_manager.broadcast("display_power_command", {
        "state": state,
        "timestamp": True,
    })

    return {
        "status": "success",
        "requested_state": state,
        "hardware_command": executed_cmd,
        "hardware_executed": cmd_success,
        "websocket_broadcast": True,
    }
