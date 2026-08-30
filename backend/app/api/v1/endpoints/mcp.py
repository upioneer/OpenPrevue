"""Model Context Protocol (MCP) REST API endpoints."""

from typing import Any
from fastapi import APIRouter, Body
from backend.app.services.mcp.server import mcp_server

router = APIRouter()


@router.post("/mcp")
async def handle_mcp_json_rpc(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Execute standard JSON-RPC 2.0 Model Context Protocol (MCP) tool and resource queries."""
    return await mcp_server.process_json_rpc(payload)


@router.get("/mcp/tools")
async def list_mcp_tools() -> dict[str, Any]:
    """Retrieve OpenAPI/JSON-Schema tool definitions exposed by OpenPrevue MCP server."""
    return {"tools": mcp_server.get_tool_definitions()}


@router.get("/mcp/resources")
async def list_mcp_resources() -> dict[str, Any]:
    """Retrieve available resource URIs exposed by OpenPrevue MCP server."""
    return {"resources": mcp_server.get_resource_definitions()}
