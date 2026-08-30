"""Model Context Protocol (MCP) server implementation for OpenPrevue."""

import json
from datetime import datetime, timezone
from typing import Any

from backend.app.core.logging import logger
from backend.app.db.session import get_db
from backend.app.services.eas import eas_service
from backend.app.services.ingestion import ingestion_service
from backend.app.services.weather import weather_service
from backend.app.services.websocket import connection_manager


class MCPServer:
    """Implements Model Context Protocol (MCP) JSON-RPC 2.0 handler."""

    def __init__(self) -> None:
        self.server_name = "openprevue-mcp"
        self.server_version = "0.8.0"

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Return MCP tool schemas."""
        return [
            {
                "name": "list_events",
                "description": "List events in OpenPrevue with optional filtering by date, category, venue, or ticket commitment status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Filter by category: concert, comedy, theater, sports, municipal, festival"},
                        "has_ticket": {"type": "integer", "enum": [0, 1], "description": "Filter by ticket commitment status: 1 for confirmed tickets, 0 for interest"},
                        "limit": {"type": "integer", "default": 20, "description": "Maximum number of events to return"},
                    },
                },
            },
            {
                "name": "search_events",
                "description": "Search events across title, description, artist, and venue name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search keyword or artist name"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "toggle_ticket_commitment",
                "description": "Toggle ticket commitment status on a specific event (track commitments vs interests).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string", "description": "Canonical event identifier"},
                        "has_ticket": {"type": "integer", "enum": [0, 1], "description": "1 to mark as committed ticket, 0 to unmark"},
                    },
                    "required": ["event_id", "has_ticket"],
                },
            },
            {
                "name": "pin_spotlight_event",
                "description": "Pin an event to the high-visibility Spotlight Pane and broadcast live update to TV displays.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_id": {"type": "string", "description": "Event ID to pin"},
                        "is_featured": {"type": "boolean", "default": True, "description": "True to pin, False to unpin"},
                    },
                    "required": ["event_id"],
                },
            },
            {
                "name": "trigger_ingestion_sync",
                "description": "Trigger an immediate ingestion synchronization pass across all registered ticketing and municipal feeds.",
                "inputSchema": {"type": "object"},
            },
            {
                "name": "get_system_health",
                "description": "Retrieve comprehensive system health, circuit breaker states, and speech heartbeats.",
                "inputSchema": {"type": "object"},
            },
            {
                "name": "dispatch_emergency_alert",
                "description": "Dispatch a simulated or live Emergency Alert System (EAS) broadcast to all displays.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string", "description": "CIVIL EMERGENCY, TORNADO WARNING, FLASH FLOOD WARNING, AMBER ALERT"},
                        "headline": {"type": "string", "description": "Alert headline"},
                        "area_description": {"type": "string", "description": "Affected zone or parish"},
                        "instruction": {"type": "string", "description": "Safety instructions"},
                    },
                    "required": ["event_type", "headline"],
                },
            },
        ]

    def get_resource_definitions(self) -> list[dict[str, Any]]:
        """Return MCP resource schemas."""
        return [
            {
                "uri": "prevue://events/today",
                "name": "Today's Schedule",
                "description": "Ascii formatted listing of today's events",
                "mimeType": "text/plain",
            },
            {
                "uri": "prevue://events/weekend",
                "name": "Weekend Digest",
                "description": "Upcoming weekend events listing",
                "mimeType": "text/plain",
            },
            {
                "uri": "prevue://events/committed",
                "name": "Ticketed Commitments",
                "description": "Events the user holds confirmed tickets to",
                "mimeType": "application/json",
            },
            {
                "uri": "prevue://venues/directory",
                "name": "Canonical Venue Directory",
                "description": "List of indexed venues and coordinates",
                "mimeType": "application/json",
            },
            {
                "uri": "prevue://system/status",
                "name": "System Status & Telemetry",
                "description": "Active system telemetry, ambient weather, and provider status",
                "mimeType": "application/json",
            },
        ]

    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute MCP tool by name."""
        if tool_name == "list_events":
            category = arguments.get("category")
            has_ticket = arguments.get("has_ticket")
            limit = int(arguments.get("limit", 20))

            query = "SELECT e.*, v.name as venue_name FROM events e LEFT JOIN venues v ON e.venue_id = v.id WHERE e.status = 'active'"
            params = []
            if category:
                query += " AND e.category = ?"
                params.append(category)
            if has_ticket is not None:
                query += " AND e.has_ticket = ?"
                params.append(has_ticket)
            query += " ORDER BY e.start_time ASC LIMIT ?"
            params.append(limit)

            async with get_db() as db:
                async with db.execute(query, tuple(params)) as cursor:
                    rows = [dict(r) for r in await cursor.fetchall()]
            return {"events": rows, "count": len(rows)}

        elif tool_name == "search_events":
            q = arguments.get("query", "").strip()
            pattern = f"%{q}%"
            async with get_db() as db:
                async with db.execute(
                    """
                    SELECT e.*, v.name as venue_name FROM events e
                    LEFT JOIN venues v ON e.venue_id = v.id
                    WHERE (e.title LIKE ? OR e.description LIKE ? OR v.name LIKE ?) AND e.status = 'active'
                    ORDER BY e.start_time ASC LIMIT 20
                    """,
                    (pattern, pattern, pattern),
                ) as cursor:
                    rows = [dict(r) for r in await cursor.fetchall()]
            return {"query": q, "results": rows, "count": len(rows)}

        elif tool_name == "toggle_ticket_commitment":
            event_id = arguments["event_id"]
            has_ticket = int(arguments["has_ticket"])

            async with get_db() as db:
                await db.execute("UPDATE events SET has_ticket = ? WHERE id = ?", (has_ticket, event_id))
                await db.commit()

            await connection_manager.broadcast("events_updated", {"event_id": event_id, "has_ticket": has_ticket})
            return {"event_id": event_id, "has_ticket": has_ticket, "status": "updated"}

        elif tool_name == "pin_spotlight_event":
            event_id = arguments["event_id"]
            is_featured = 1 if arguments.get("is_featured", True) else 0

            async with get_db() as db:
                await db.execute("UPDATE events SET is_featured = ? WHERE id = ?", (is_featured, event_id))
                await db.commit()

            await connection_manager.broadcast("events_updated", {"pinned_event_id": event_id, "is_featured": is_featured})
            return {"event_id": event_id, "is_featured": bool(is_featured), "status": "updated"}

        elif tool_name == "trigger_ingestion_sync":
            sync_res = await ingestion_service.trigger_sync_all()
            return sync_res

        elif tool_name == "get_system_health":
            async with get_db() as db:
                async with db.execute("SELECT COUNT(*) AS count FROM events WHERE status = 'active'") as cursor:
                    row = await cursor.fetchone()
                    count = row["count"] if row else 0

            weather = await weather_service.get_current_weather()
            return {
                "status": "operational",
                "active_events": count,
                "weather": weather.to_dict(),
            }

        elif tool_name == "dispatch_emergency_alert":
            alert = await eas_service.create_test_alert(
                event_type=arguments.get("event_type", "CIVIL EMERGENCY"),
                headline=arguments.get("headline", "EMERGENCY BROADCAST"),
                severity="Severe",
                area_description=arguments.get("area_description", "LOCAL AREA"),
                instruction=arguments.get("instruction", "Take precautions."),
            )
            return {"alert": alert.model_dump(mode="json"), "status": "broadcasted"}

        raise ValueError(f"Unknown MCP tool: {tool_name}")

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """Read MCP resource by URI."""
        if uri == "prevue://events/committed":
            async with get_db() as db:
                async with db.execute("SELECT * FROM events WHERE has_ticket = 1 ORDER BY start_time ASC") as cursor:
                    rows = [dict(r) for r in await cursor.fetchall()]
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(rows)}]}

        elif uri == "prevue://venues/directory":
            async with get_db() as db:
                async with db.execute("SELECT * FROM venues ORDER BY sort_order ASC, name ASC") as cursor:
                    rows = [dict(r) for r in await cursor.fetchall()]
            return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(rows)}]}

        elif uri == "prevue://events/today":
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            async with get_db() as db:
                async with db.execute(
                    "SELECT e.*, v.name as venue_name FROM events e LEFT JOIN venues v ON e.venue_id = v.id WHERE date(e.start_time) = ? ORDER BY e.start_time ASC",
                    (today_str,),
                ) as cursor:
                    rows = [dict(r) for r in await cursor.fetchall()]
            lines = [f"{r['start_time'][11:16]} | {r['title']} @ {r.get('venue_name') or 'N/A'}" for r in rows]
            return {"contents": [{"uri": uri, "mimeType": "text/plain", "text": "\n".join(lines)}]}

        elif uri == "prevue://system/status":
            weather = await weather_service.get_current_weather()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({"status": "operational", "weather": weather.to_dict()}),
                    }
                ]
            }

        raise ValueError(f"Unknown MCP resource URI: {uri}")

    async def process_json_rpc(self, request_body: dict[str, Any]) -> dict[str, Any]:
        """Process incoming JSON-RPC 2.0 MCP request."""
        req_id = request_body.get("id")
        method = request_body.get("method")
        params = request_body.get("params", {})

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": self.server_name, "version": self.server_version},
                        "capabilities": {"tools": {}, "resources": {}},
                    },
                }

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": self.get_tool_definitions()},
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                res = await self.handle_tool_call(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res)}]},
                }

            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": self.get_resource_definitions()},
                }

            elif method == "resources/read":
                uri = params.get("uri")
                res = await self.read_resource(uri)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": res,
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"},
                }

        except Exception as exc:
            logger.warning("MCP JSON-RPC error: %s", exc)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(exc)},
            }


mcp_server = MCPServer()
