"""Test settings API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.db.session import init_db, get_db
from backend.app.services.seeder import seed_initial_data


@pytest.fixture(autouse=True)
async def setup_database():
    """Initialize database and default settings."""
    await init_db()
    async with get_db() as db:
        await db.execute("DELETE FROM settings WHERE key LIKE 'test_%' OR key LIKE 'ultrawide_%' OR key LIKE 'spotlight_%' OR key LIKE 'youtube_%'")
        await db.commit()
    await seed_initial_data()


@pytest.mark.asyncio
async def test_get_settings():
    """Verify settings retrieval returns dictionary of configuration parameters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        assert "postal_code" in data
        assert "radius_miles" in data
        assert "autoscroll_speed" in data
        assert data["autoscroll_speed"] == "30"


@pytest.mark.asyncio
async def test_update_setting():
    """Verify updating a setting persists in the datastore."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/settings/test_setting_key",
            json={"value": "test_value_123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test_setting_key"
        assert data["value"] == "test_value_123"

        # Verify on get
        get_res = await client.get("/api/v1/settings")
        assert get_res.json()["test_setting_key"] == "test_value_123"
        # Ensure autoscroll_speed remains 30
        assert get_res.json()["autoscroll_speed"] == "30"


@pytest.mark.asyncio
async def test_ultrawide_settings_defaults_and_updates():
    """Verify ultrawide mode and priority defaults and updating capabilities."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check initial seeded defaults
        res = await client.get("/api/v1/settings")
        assert res.status_code == 200
        settings = res.json()
        assert settings.get("ultrawide_mode") == "auto"
        assert settings.get("ultrawide_priority") == "calendar"

        # Update priority to 'feature'
        update_res = await client.put(
            "/api/v1/settings/ultrawide_priority",
            json={"value": "feature"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["value"] == "feature"

        # Update mode to 'always'
        update_mode_res = await client.put(
            "/api/v1/settings/ultrawide_mode",
            json={"value": "always"},
        )
        assert update_mode_res.status_code == 200
        assert update_mode_res.json()["value"] == "always"

        # Verify persisted values
        get_res = await client.get("/api/v1/settings")
        assert get_res.json()["ultrawide_priority"] == "feature"
        assert get_res.json()["ultrawide_mode"] == "always"


@pytest.mark.asyncio
async def test_youtube_spotlight_settings_defaults_and_updates():
    """Verify spotlight mode, youtube aspect ratio, audio mode, and shuffle defaults and updates."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/settings")
        assert res.status_code == 200
        settings = res.json()
        assert settings.get("spotlight_mode") == "featured"
        assert settings.get("youtube_audio_mode") == "mute"
        assert settings.get("youtube_aspect_ratio") == "4:3"
        assert settings.get("youtube_shuffle_enabled") == "0"

        # Update spotlight mode to 'youtube'
        await client.put("/api/v1/settings/spotlight_mode", json={"value": "youtube"})
        await client.put("/api/v1/settings/youtube_source_url", json={"value": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        await client.put("/api/v1/settings/youtube_aspect_ratio", json={"value": "16:9"})
        await client.put("/api/v1/settings/youtube_audio_mode", json={"value": "audio"})
        await client.put("/api/v1/settings/youtube_shuffle_enabled", json={"value": "1"})

        get_res = await client.get("/api/v1/settings")
        data = get_res.json()
        assert data["spotlight_mode"] == "youtube"
        assert data["youtube_source_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert data["youtube_aspect_ratio"] == "16:9"
        assert data["youtube_audio_mode"] == "audio"
        assert data["youtube_shuffle_enabled"] == "1"
