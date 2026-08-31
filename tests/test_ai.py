"""Tests for AI and Ollama local model connectivity endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_ollama_ping_offline_graceful():
    """Verify that probing an unreachable Ollama instance returns a graceful offline response without crashing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/ai/ollama/ping",
            json={"ollama_url": "http://127.0.0.1:59999", "model": "llama3.2"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "offline"
        assert data["ollama_url"] == "http://127.0.0.1:59999"
        assert "Connection refused" in data["error"] or "timed out" in data["error"]
        assert isinstance(data["latency_ms"], int)
        assert data["models"] == []


@pytest.mark.asyncio
async def test_ollama_ping_default_payload():
    """Verify standard default payload validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/ai/ollama/ping",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ollama_url"] == "http://localhost:11434"
