# Release v0.1.0: Foundations and Baseline Architecture

## Overview
Initial release establishing the complete baseline architecture for OpenPrevue, including the asynchronous Python FastAPI backend, SQLite WAL datastore, mock event ingestion engine, Vue 3 retro channel guide frontend, and container deployment configuration.

## Key Deliverables

### 1. Asynchronous FastAPI Backend
* SQLite 3 storage engine configured with Write Ahead Logging (WAL) and foreign key enforcement.
* Full schema initialization for venues, venue aliases, events, ticket links, ingestion logs, telegram users, and watchlists.
* REST API endpoints under `/api/v1/` for health observability, events, venues, dynamic settings, and manual sync triggers.
* Pydantic v2 data validation schemas and structured stdout logging.

### 2. Ingestion and Normalization Engine
* Abstract `BaseProvider` interface and provider registry.
* `MockEventProvider` generating realistic time anchored local listings across New Orleans venues (Caesars Superdome, House of Blues, Saenger Theatre, Tipitina's, Fillmore NOLA, Joy Theater, Smoothie King Center).
* Haversine geographic radial filtering, canonical venue slug generation, and temporal event deduplication with multi source purchase link fusion.
* Ingestion audit logging tracking fetch, insert, update, and skip counts per execution.

### 3. Retro 1990s Prevue UI Frontend
* Vue 3 Single Page Application styled with Vite and Tailwind CSS v4.
* Hardware composited CRT scanline overlay and phosphor glow shaders.
* Top 45% `SpotlightPane` featuring promotional media, metadata bulletin, dynamic QR code checkout generation, and auto rotation.
* Middle `DividerRibbon` with real time digital clock, weather indicators, metro area badge, and search radius display.
* Bottom 50% `TimelineGrid` with continuous virtual autoscroll categorized into Today, Tonight, and Tomorrow time slots with category indicator pips.
* Dedicated `SettingsView` for runtime configuration adjustments without restarting the service.

### 4. Containerization and Parity
* Multi stage `Dockerfile` packaging Node build stage into Debian slim Python runtime.
* `docker-compose.yml` defining production container parameters, volume mounts, resource limits, and healthcheck probes.
* Static single port SPA mounting allowing monolithic deployment behind a single port.

### 5. Automated Verification
* 10 automated backend integration and unit tests passing in pytest.
* Zero error TypeScript and Vite production bundle compilation.
