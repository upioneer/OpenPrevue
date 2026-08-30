"""Emergency Alert System (EAS) ingestion service for NWS, USGS, and civil safety bulletins."""

from datetime import datetime, timezone
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.schemas.eas import EmergencyAlert
from backend.app.services.websocket import connection_manager


class EASService:
    """Ingests, parses, and broadcasts emergency alert notifications."""

    def __init__(self) -> None:
        self.active_alerts: dict[str, EmergencyAlert] = {}
        self.seen_alert_ids: set[str] = set()

    async def get_eas_settings(self) -> dict[str, str]:
        """Fetch EAS configuration flags from database settings."""
        async with get_db() as db:
            async with db.execute(
                "SELECT key, value FROM settings WHERE key IN ('eas_enabled', 'eas_severity_threshold', 'eas_display_duration_seconds', 'eas_sound_enabled', 'latitude', 'longitude', 'radius_miles')"
            ) as cursor:
                rows = await cursor.fetchall()
                return {row["key"]: row["value"] for row in rows}

    async def fetch_nws_alerts(self, latitude: float, longitude: float) -> list[EmergencyAlert]:
        """Fetch active meteorological warnings from National Weather Service (NWS) CAP API."""
        url = f"https://api.weather.gov/alerts/active?point={latitude:.4f},{longitude:.4f}"
        headers = {
            "User-Agent": "OpenPrevue/0.7.0 (contact@openprevue.org)",
            "Accept": "application/geo+json, application/json",
        }
        alerts: list[EmergencyAlert] = []

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    features = data.get("features", [])

                    for item in features:
                        props = item.get("properties", {})
                        alert_id = props.get("id") or item.get("id")
                        if not alert_id:
                            continue

                        event_type = props.get("event", "SEVERE WEATHER WARNING").upper()
                        headline = props.get("headline") or f"{event_type} in effect for local area."
                        severity = props.get("severity", "Severe")
                        urgency = props.get("urgency", "Immediate")
                        area_desc = props.get("areaDesc", "Local Area")
                        instruction = props.get("instruction") or props.get("description", "Take appropriate precautions.")
                        effective = props.get("effective") or datetime.now(timezone.utc).isoformat()
                        expires = props.get("expires") or datetime.now(timezone.utc).isoformat()

                        alert = EmergencyAlert(
                            id=str(alert_id),
                            sender=props.get("senderName", "National Weather Service"),
                            headline=headline,
                            severity=severity,
                            urgency=urgency,
                            event_type=event_type,
                            area_description=area_desc,
                            instruction=instruction,
                            effective_at=str(effective),
                            expires_at=str(expires),
                            is_active=True,
                        )
                        alerts.append(alert)
        except Exception as exc:
            logger.debug("Error querying NWS active alerts: %s", exc)

        return alerts

    async def poll_and_broadcast_alerts(self) -> list[EmergencyAlert]:
        """Poll active emergency feeds and broadcast newly detected threats."""
        try:
            cfg = await self.get_eas_settings()
            if cfg.get("eas_enabled", "1") != "1":
                return list(self.active_alerts.values())

            lat = float(cfg.get("latitude", settings.DEFAULT_LATITUDE))
            lon = float(cfg.get("longitude", settings.DEFAULT_LONGITUDE))

            nws_alerts = await self.fetch_nws_alerts(lat, lon)
            current_active: dict[str, EmergencyAlert] = dict(self.active_alerts)

            for alert in nws_alerts:
                current_active[alert.id] = alert
                if alert.id not in self.seen_alert_ids:
                    self.seen_alert_ids.add(alert.id)
                    logger.info("New EAS Emergency Alert detected: [%s] %s", alert.event_type, alert.headline)
                    await connection_manager.broadcast("emergency_alert", alert.model_dump(mode="json"))

            self.active_alerts = current_active
        except Exception as exc:
            logger.debug("Error polling EAS alerts: %s", exc)

        return list(self.active_alerts.values())

    async def create_test_alert(
        self,
        event_type: str = "CIVIL EMERGENCY",
        headline: str = "EMERGENCY BROADCAST SYSTEM TEST - LOCAL AREA",
        severity: str = "Severe",
        area_description: str = "LOCAL RECEPTION AREA",
        instruction: str = "This is a test of the OpenPrevue Emergency Alert System. No action is required.",
        duration_seconds: int = 30,
    ) -> EmergencyAlert:
        """Generate and broadcast an instant simulated EAS emergency alert."""
        now_iso = datetime.now(timezone.utc).isoformat()
        test_id = f"eas-test-{int(datetime.now(timezone.utc).timestamp())}"

        alert = EmergencyAlert(
            id=test_id,
            sender="OPENPREVUE EMERGENCY BROADCAST TEST",
            headline=headline,
            severity=severity,
            urgency="Immediate",
            event_type=event_type.upper(),
            area_description=area_description,
            instruction=instruction,
            effective_at=now_iso,
            expires_at=now_iso,
            is_active=True,
        )

        self.active_alerts[test_id] = alert
        logger.info("Broadcasting simulated EAS test alert: %s", alert.headline)
        await connection_manager.broadcast("emergency_alert", alert.model_dump(mode="json"))
        return alert


eas_service = EASService()
