"""Home Assistant entity status aggregator, MQTT auto-discovery, and REST sensor engine."""

from datetime import datetime, timezone
import json
import time
from typing import Any
import aiosqlite

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.services.weather import weather_service

START_TIME = time.time()


class HomeAssistantService:
    """Aggregates OpenPrevue entity states for Home Assistant REST sensors and MQTT Discovery."""

    async def get_sensor_payload(self) -> dict[str, Any]:
        """Aggregate comprehensive status payload for Home Assistant REST sensor integration."""
        uptime = round(time.time() - START_TIME, 1)

        # 1. Query events and spotlight status
        active_count = 0
        committed_count = 0
        today_events: list[dict[str, Any]] = []
        spotlight_event: dict[str, Any] | None = None
        metro_label = settings.DEFAULT_METRO_LABEL

        now_utc = datetime.now(timezone.utc)
        today_prefix = now_utc.strftime("%Y-%m-%d")

        try:
            async with get_db() as db:
                # Get metro label
                async with db.execute("SELECT value FROM settings WHERE key = 'metro_label'") as cursor:
                    row = await cursor.fetchone()
                    if row and row["value"]:
                        metro_label = row["value"]

                # Count active events
                async with db.execute("SELECT COUNT(*) AS c FROM events WHERE status = 'active'") as cursor:
                    row = await cursor.fetchone()
                    active_count = row["c"] if row else 0

                # Count committed tickets
                async with db.execute("SELECT COUNT(*) AS c FROM events WHERE status = 'active' AND has_ticket = 1") as cursor:
                    row = await cursor.fetchone()
                    committed_count = row["c"] if row else 0

                # Get spotlight event
                async with db.execute(
                    """
                    SELECT e.id, e.title, e.category, e.start_time, e.price_min, e.price_max, e.ticket_url, e.image_url, v.name AS venue_name
                    FROM events e
                    JOIN venues v ON e.venue_id = v.id
                    WHERE e.status = 'active' AND e.is_featured = 1
                    ORDER BY e.start_time ASC
                    LIMIT 1
                    """
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        spotlight_event = dict(row)

                # Get today's events list
                async with db.execute(
                    """
                    SELECT e.id, e.title, e.category, e.start_time, e.has_ticket, v.name AS venue_name
                    FROM events e
                    JOIN venues v ON e.venue_id = v.id
                    WHERE e.status = 'active' AND e.start_time LIKE ?
                    ORDER BY e.start_time ASC
                    LIMIT 20
                    """,
                    (f"{today_prefix}%",),
                ) as cursor:
                    rows = await cursor.fetchall()
                    today_events = [dict(r) for r in rows]
        except Exception as exc:
            logger.error("Error querying Home Assistant sensor state: %s", exc)

        # 2. Get live weather
        weather = await weather_service.get_current_weather()

        # 3. Check EAS Alert status
        eas_active = False
        eas_headline = ""
        eas_severity = "none"
        try:
            async with get_db() as db:
                async with db.execute(
                    "SELECT event, headline, severity FROM emergency_alerts WHERE expires_at > ? ORDER BY id DESC LIMIT 1",
                    (now_utc.isoformat(),),
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        eas_active = True
                        eas_headline = row["headline"] or row["event"]
                        eas_severity = row["severity"] or "alert"
        except Exception:
            pass

        return {
            "status": "operational",
            "version": "0.18.0",
            "uptime_seconds": uptime,
            "metro_label": metro_label,
            "counts": {
                "active_events": active_count,
                "committed_tickets": committed_count,
                "today_events_count": len(today_events),
            },
            "today_events": today_events,
            "spotlight": spotlight_event or {
                "title": "OpenPrevue Retro Guide",
                "venue_name": metro_label,
                "category": "broadcast",
            },
            "weather": {
                "temperature": weather.temperature,
                "condition": weather.condition,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "temperature_unit": weather.temperature_unit,
            },
            "eas": {
                "is_active": eas_active,
                "headline": eas_headline,
                "severity": eas_severity,
            },
        }

    def generate_yaml_configuration(self, base_url: str = "http://localhost:8080") -> str:
        """Generate ready-to-paste Home Assistant YAML snippet for configuration.yaml."""
        return f"""# ====================================================================
# OpenPrevue Home Assistant Integration (configuration.yaml)
# ====================================================================
rest:
  - resource: "{base_url}/api/v1/integrations/homeassistant/sensors"
    scan_interval: 60
    sensor:
      - name: "OpenPrevue Today Events Count"
        value_template: "{{{{ value_json.counts.today_events_count }}}}"
        icon: "mdi:calendar-star"
        unit_of_measurement: "events"

      - name: "OpenPrevue Active Spotlight"
        value_template: "{{{{ value_json.spotlight.title }}}}"
        icon: "mdi:television-classic"
        json_attributes_path: "$.spotlight"
        json_attributes:
          - venue_name
          - category
          - start_time
          - price_min

      - name: "OpenPrevue Committed Tickets"
        value_template: "{{{{ value_json.counts.committed_tickets }}}}"
        icon: "mdi:ticket-confirmation"
        unit_of_measurement: "tickets"

      - name: "OpenPrevue Weather Condition"
        value_template: "{{{{ value_json.weather.condition }}}}"
        icon: "mdi:weather-partly-cloudy"
        json_attributes_path: "$.weather"
        json_attributes:
          - temperature
          - humidity
          - wind_speed

    binary_sensor:
      - name: "OpenPrevue EAS Alert Active"
        value_template: "{{{{ value_json.eas.is_active }}}}"
        device_class: "safety"
        icon: "mdi:alert-decagram"
        json_attributes_path: "$.eas"
        json_attributes:
          - headline
          - severity
"""


homeassistant_service = HomeAssistantService()
