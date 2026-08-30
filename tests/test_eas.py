"""Unit and integration tests for Emergency Alert System (EAS) services and endpoints."""

from unittest.mock import patch
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.schemas.eas import EmergencyAlert
from backend.app.services.eas import eas_service


@pytest.mark.asyncio
async def test_eas_create_test_alert():
    """Verify test alert creation and state assignment."""
    alert = await eas_service.create_test_alert(
        event_type="TORNADO WARNING",
        headline="TORNADO WARNING FOR ORLEANS PARISH",
        severity="Extreme",
        area_description="Orleans Parish, LA",
        instruction="TAKE SHELTER IMMEDIATELY.",
        duration_seconds=45,
    )
    assert alert.event_type == "TORNADO WARNING"
    assert alert.severity == "Extreme"
    assert alert.id.startswith("eas-test-")
    assert alert.is_active is True
    assert alert.id in eas_service.active_alerts


@pytest.mark.asyncio
async def test_eas_api_endpoints():
    """Verify EAS REST API endpoints for fetching alerts and dispatching simulations."""
    mock_alert = EmergencyAlert(
        id="nws-mock-1",
        sender="National Weather Service",
        headline="TORNADO WARNING FOR LOCAL AREA",
        severity="Extreme",
        urgency="Immediate",
        event_type="TORNADO WARNING",
        area_description="Local Parish",
        instruction="Take shelter now.",
        effective_at="2026-08-30T18:00:00Z",
        expires_at="2026-08-30T20:00:00Z",
        is_active=True,
    )

    with patch.object(eas_service, "fetch_nws_alerts", return_value=[mock_alert]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # POST /api/v1/eas/test
            payload = {
                "event_type": "CIVIL EMERGENCY",
                "headline": "CIVIL EMERGENCY MESSAGE - TEST",
                "severity": "Severe",
                "area_description": "ORLEANS PARISH",
                "instruction": "Test instruction",
                "duration_seconds": 30,
            }
            res_test = await client.post("/api/v1/eas/test", json=payload)
            assert res_test.status_code == 200
            data = res_test.json()
            assert data["event_type"] == "CIVIL EMERGENCY"
            assert data["headline"] == "CIVIL EMERGENCY MESSAGE - TEST"

            # GET /api/v1/eas/alerts
            res_list = await client.get("/api/v1/eas/alerts")
            assert res_list.status_code == 200
            alerts = res_list.json()
            assert isinstance(alerts, list)
            assert any(a["id"] == "nws-mock-1" for a in alerts)
