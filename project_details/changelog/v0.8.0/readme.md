# Release v0.8.0: Model Context Protocol (MCP) & Agent Client Protocol (ACP)

## Overview
Release v0.8.0 introduces an embedded Model Context Protocol (MCP) server, enabling autonomous AI coding agents, IDE assistants, and external automated orchestrators to query local event listings, curate spotlight carousels, toggle ticket commitments, and trigger ingestion pipelines.

## Key Deliverables

### 1. Embedded Model Context Protocol (MCP) Server (`mcp/server.py`)
* **JSON-RPC 2.0 Engine:** Full support for standard MCP transports over HTTP (`POST /api/v1/mcp`).
* **MCP Tools Suite:**
  * `list_events`: Filter events by category, venue, and ticket commitment status.
  * `search_events`: Keyword and performer search across canonical index.
  * `toggle_ticket_commitment`: Programmatic ticket commitment status updates (`has_ticket=1/0`).
  * `pin_spotlight_event`: Remote spotlight pinning broadcasting live WebSocket triggers to displays.
  * `trigger_ingestion_sync`: Immediate synchronization pass across all registered providers.
  * `get_system_health`: Real-time system telemetry and provider circuit breaker diagnostics.
  * `dispatch_emergency_alert`: Simulated or live EAS alert broadcast.

### 2. MCP Resource Providers (`resources/list`, `resources/read`)
* `prevue://events/today`: Formatted ASCII bulletin of today's schedule.
* `prevue://events/weekend`: Upcoming weekend listings.
* `prevue://events/committed`: Verified ticketed commitments.
* `prevue://venues/directory`: Canonical venue index and coordinates.
* `prevue://system/status`: Real-time telemetry, ambient weather, and uptime.

### 3. Agent Client Protocol (ACP) & REST Endpoints
* `POST /api/v1/mcp`: Main JSON-RPC 2.0 processor.
* `GET /api/v1/mcp/tools`: OpenAPI/JSON-schema tool catalog.
* `GET /api/v1/mcp/resources`: MCP resource directory.

### 4. Automated Verification
* 47 passing tests in pytest across MCP handshake, tool calling, resource reading, EAS ingestion, and speech pipelines.
* Zero error TypeScript compilation and Vite frontend production bundle.
