"""Unit and integration tests for Model Context Protocol (MCP) server and endpoints."""

import json
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.services.mcp.server import mcp_server


@pytest.mark.asyncio
async def test_mcp_initialize():
    """Verify MCP initialize handshake returns server capability descriptor."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
        res = await client.post("/api/v1/mcp", json=req)
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == 1
        assert data["result"]["serverInfo"]["name"] == "openprevue-mcp"
        assert "tools" in data["result"]["capabilities"]


@pytest.mark.asyncio
async def test_mcp_tools_list():
    """Verify MCP tools/list returns available agent tools."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        res = await client.post("/api/v1/mcp", json=req)
        assert res.status_code == 200
        data = res.json()
        tools = data["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        assert "list_events" in tool_names
        assert "search_events" in tool_names
        assert "toggle_ticket_commitment" in tool_names
        assert "pin_spotlight_event" in tool_names
        assert "get_system_health" in tool_names


@pytest.mark.asyncio
async def test_mcp_tool_call_list_and_toggle_ticket():
    """Verify MCP tools/call executes tool actions in SQLite."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Call list_events
        list_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "list_events", "arguments": {"limit": 5}},
        }
        res = await client.post("/api/v1/mcp", json=list_req)
        assert res.status_code == 200
        payload = json.loads(res.json()["result"]["content"][0]["text"])
        assert payload["count"] > 0
        target_event_id = payload["events"][0]["id"]

        # Call toggle_ticket_commitment
        toggle_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "toggle_ticket_commitment",
                "arguments": {"event_id": target_event_id, "has_ticket": 1},
            },
        }
        toggle_res = await client.post("/api/v1/mcp", json=toggle_req)
        assert toggle_res.status_code == 200
        toggle_data = json.loads(toggle_res.json()["result"]["content"][0]["text"])
        assert toggle_data["has_ticket"] == 1


@pytest.mark.asyncio
async def test_mcp_resources_list_and_read():
    """Verify MCP resources/list and resources/read."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # resources/list
        list_res = await client.post("/api/v1/mcp", json={"jsonrpc": "2.0", "id": 5, "method": "resources/list"})
        assert list_res.status_code == 200
        resources = list_res.json()["result"]["resources"]
        uris = [r["uri"] for r in resources]
        assert "prevue://events/committed" in uris
        assert "prevue://system/status" in uris

        # resources/read
        read_res = await client.post(
            "/api/v1/mcp",
            json={"jsonrpc": "2.0", "id": 6, "method": "resources/read", "params": {"uri": "prevue://system/status"}},
        )
        assert read_res.status_code == 200
        content = read_res.json()["result"]["contents"][0]
        assert content["uri"] == "prevue://system/status"
        status_obj = json.loads(content["text"])
        assert status_obj["status"] == "operational"
