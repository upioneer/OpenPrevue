# Release v0.5.0: Settings Management, Retro Shaders & Speech Heartbeats

## Overview
Release v0.5.0 introduces a comprehensive tabbed retro control center in the web UI, live speech engine health monitoring and latency heartbeat telemetry, interactive Telegram account pairing tables, and configurable CRT video shaders and background Spotify audio streams.

## Key Deliverables

### 1. Tabbed Retro Control Center
* **Navigation Tabs:** Five dedicated functional sections (`Location & Discovery`, `Retro CRT Shader`, `Spotify & Muzak`, `Telegram & Speech`, `Provider Feeds`).
* **Location & Radial Aggregation:** Configurable metro area label, postal code, coordinate center, search radius slider (5 to 100 miles), and ingestion interval.
* **Provider Feeds & Circuit Breakers:** Real time status cards for all registered providers (Ticketmaster, SeatGeek, Eventbrite, JSON-LD, iCal, Weather) with circuit breaker state badges (`CLOSED`, `OPEN`, `HALF_OPEN`), cached count, and last sync timestamp.

### 2. Speech Engine Heartbeat & Health Monitoring
* **Speech Service (`speech.py`):** Real time monitoring of speech pipeline operational status, active engine mode (`local_standard` vs `enhanced_cloud`), active STT/TTS models, and timestamped heartbeat probes.
* **Diagnostic Testing Endpoints:**
  * `GET /api/v1/speech/status`: Returns current engine mode, STT/TTS status, latency, and heartbeat.
  * `POST /api/v1/speech/test`: Triggers active audio round-trip diagnostic test and measures round-trip latency in milliseconds.
* **System Health Integration:** Mounted speech status into the master `GET /api/v1/health` response.

### 3. Telegram Account & Device Management
* **Pairing Code Generator:** 1-click button generating random 6-character ephemeral pairing tokens (`PREVUE-XXXX`) with countdown timer.
* **Connected Accounts Table:** Displays paired chat IDs, usernames, and authentication timestamps with 1-click unpair and "Send Test Message" buttons.
* **Speech Enhancement Configuration:** Dedicated "Improve Voice Capabilities" inputs for optional Groq and ElevenLabs API keys with automatic cloud routing and local fallback.

### 4. Retro Shaders & Audio Controls
* **CRT Visual Shaders:** Real time toggles and sliders for CRT horizontal scanline intensity, phosphor text bloom, barrel curvature distortion, and analog VHS tracking jitter.
* **Audio Controls:** Spotify background autoplay toggle, custom playlist URI input, public 90s weather channel fallback stream, and Web Audio analog cassette tape hiss generator.

### 5. Automated Verification
* 39 passing tests in pytest across speech service health, diagnostic probes, speech REST API endpoints, Telegram formatters, and provider adapters.
* Zero error TypeScript compilation and Vite frontend production bundle.
