# Release v0.3.0: Live Weather & Real-Time WebSocket Synchronization

## Overview
Release v0.3.0 introduces live ambient weather telemetry from Open-Meteo into the 90s Prevue Divider Ribbon and integrates a real-time bidirectional WebSocket event broadcaster (`/ws/dashboard`) for instant multi-client dashboard state synchronization without requiring page reloads.

## Key Deliverables

### 1. Live Weather Aggregation Service
* **Open-Meteo Integration:** Fetches ambient temperature (°F), apparent temperature, humidity, wind speed, and WMO weather codes using coordinates from SQLite settings.
* **WMO Code Translator:** Translates numeric WMO codes into retro uppercase condition strings (`CLEAR SKY`, `PARTLY CLOUDY`, `OVERCAST`, `SLIGHT RAIN`, `THUNDERSTORM`, etc.).
* **15-Minute In-Memory Caching:** High-efficiency cache preventing external rate limiting with automatic background refresh triggers in APScheduler.
* **REST Endpoints:** `GET /api/v1/weather` for telemetry and `POST /api/v1/weather/refresh` for forced refreshes.

### 2. Real-Time WebSocket State Broadcaster
* **Bidirectional WebSocket Endpoint:** Mounted at both `/ws/dashboard` and `/api/v1/ws/dashboard`.
* **Connection Manager:** Tracks active connected displays, delivers initial `connection_ack` handshakes with live weather telemetry, and responds to client `ping` heartbeats with timestamped `pong` frames.
* **Reactive State Broadcasting:**
  * `weather_updated`: Dispatched every 15 minutes or upon manual weather refresh.
  * `events_updated`: Dispatched immediately when ingestion sync completes or events are modified.
  * `settings_updated`: Dispatched when system or display settings are modified via API or web UI.

### 3. Frontend Real-Time Ticker & Connection Manager
* **`DividerRibbon.vue`:** Displays live ambient temperature in °F, condition description, humidity percentage, wind speed in mph, digital clock, metro label, and active radius.
* **`wsService`:** Frontend WebSocket manager with exponential reconnection backoff (2s up to 30s) and 25-second heartbeat monitor.
* **Instant Reactive UI Updates:** Automatically updates event grids, spotlight cards, and CRT shaders across all connected screens the instant changes occur on the backend.

### 4. Automated Verification
* 29 passing tests in pytest across weather mappings, weather REST endpoints, WebSocket connection manager, handshake ack, and existing provider adapters.
* Zero error TypeScript compilation and Vite frontend production bundle.
