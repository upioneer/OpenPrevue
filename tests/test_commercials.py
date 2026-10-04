"""Unit and integration tests for commercial video dropzones and stream endpoints."""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app

COMMERCIALS_DIR = Path("data") / "commercials"


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Ensure mock test commercial files are never left on disk after test runs."""
    yield
    test_files = ["test_promo.mp4", "stream_test.mp4", "delete_test.mp4"]
    for fname in test_files:
        p = COMMERCIALS_DIR / fname
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass


@pytest.mark.asyncio
async def test_list_commercial_clips():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/commercials")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "dropzone_directory" in data
        assert "specifications" in data
        assert data["specifications"]["max_file_size_mb"] == 50


@pytest.mark.asyncio
async def test_upload_commercial_clip_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Rejects unsupported extension
        files = {"file": ("unsupported.txt", b"dummy content", "text/plain")}
        res_invalid = await ac.post("/api/v1/commercials/upload", files=files)
        assert res_invalid.status_code == 400

        # Accepts valid mp4 file
        valid_files = {"file": ("test_promo.mp4", b"dummy video bytes for test", "video/mp4")}
        res_valid = await ac.post("/api/v1/commercials/upload", files=valid_files)
        assert res_valid.status_code == 200
        data = res_valid.json()
        assert data["status"] == "success"
        assert data["clip"]["filename"] == "test_promo.mp4"


@pytest.mark.asyncio
async def test_stream_commercial_clip():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Seed test file via upload
        valid_files = {"file": ("stream_test.mp4", b"video stream sample data", "video/mp4")}
        await ac.post("/api/v1/commercials/upload", files=valid_files)

        # Stream existing file
        res_stream = await ac.get("/api/v1/commercials/stream/stream_test.mp4")
        assert res_stream.status_code == 200
        assert res_stream.headers["content-type"] == "video/mp4"

        # Missing file returns 404
        res_missing = await ac.get("/api/v1/commercials/stream/non_existent.mp4")
        assert res_missing.status_code == 404


@pytest.mark.asyncio
async def test_delete_commercial_clip():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Upload a clip to delete
        valid_files = {"file": ("delete_test.mp4", b"to be deleted", "video/mp4")}
        res_up = await ac.post("/api/v1/commercials/upload", files=valid_files)
        assert res_up.status_code == 200

        # Delete existing file
        res_del = await ac.delete("/api/v1/commercials/delete_test.mp4")
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "success"

        # Deleting non-existent file returns 404
        res_del_404 = await ac.delete("/api/v1/commercials/non_existent_clip.mp4")
        assert res_del_404.status_code == 404
