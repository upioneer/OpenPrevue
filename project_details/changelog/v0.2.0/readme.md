# Release v0.2.0: Ingestion Pipeline Expansion & Fault Isolation

## Overview
Release v0.2.0 expands the OpenPrevue ingestion pipeline with real world ticketing API adapters, direct venue scrapers, calendar subscription feeds, sports and motorsport taxonomy classification, ticket commitment tracking, a three state circuit breaker for external fault isolation, and an asynchronous background scheduler for automated recurring synchronizations.

## Key Deliverables

### 1. Ingestion Provider Adapters
* **Ticketmaster Discovery API & Live Nation:** Radial geographic coordinate querying (`latlong`, `radius`), classification hierarchy category mapping, price range extraction, and highest resolution promotional image selection.
* **SeatGeek Platform API:** Geolocated venue cluster queries, performer taxonomy mapping, lowest and highest secondary market price extraction, and score based featured weighting.
* **Eventbrite API:** Local organization and coordinate bounding search with structured venue and ticket availability parsing.
* **Direct Venue JSON-LD Extractor:** Async HTTP scraper extracting schema.org `@type: Event` script tags from standalone venue calendar pages with support for nested `@graph` items.
* **iCal (.ics) Calendar Subscription Parser:** RFC 5545 calendar stream parser supporting `.ics` and `webcal://` subscription feeds for municipal and performing arts venues.

### 2. Ticket Commitment Tracking & Interactive UI
* Monospaced retro `[TICKET]` badge in glowing phosphor green (`#00FF00`) indicating confirmed commitments vs general interest.
* Interactive 1-click commitment toggle (`[+TKT]` / `[TICKET]`) in the live scrolling channel grid and `[TICKET HOLDER]` banner in the featured spotlight card.
* Supported by `has_ticket` SQLite database column, automatic schema migration, and `PATCH /api/v1/events/{id}` API endpoint.

### 3. Sports & Motorsport Taxonomy Classification
* Dedicated classifier keywords across all providers for Major Sports Leagues: NFL, NBA, MLB, MLS.
* Dedicated classifier keywords for Motorsports: Formula 1 (Grand Prix), NASCAR, IndyCar, MotoGP.
* Planned connectors matrix updated for secondary ticketing platforms (Vivid Seats, StubHub, Viagogo, Tixel, Tixr) and tourism/experience manual & email import workflows (TripAdvisor, Viator).

### 4. Fault Tolerance & Circuit Breaker
* `CircuitBreaker` state machine managing `CLOSED`, `OPEN`, and `HALF_OPEN` states.
* Configurable failure threshold (5 consecutive errors) and exponential backoff recovery timer (15 minutes to 2 hours) isolating flaky external APIs without blocking application execution.

### 5. Background Synchronization Engine
* Integrated `APScheduler` (`AsyncIOScheduler`) running recurring ingestion synchronization in the background.
* Reads `sync_interval_hours` from SQLite settings and supports dynamic on the fly job rescheduling when settings are updated in the web UI.

### 6. AI Agent Integration Blueprints (MCP & ACP)
* Scoped specifications for embedded Model Context Protocol (MCP) server exposing tools (`list_events`, `search_events`, `toggle_ticket_commitment`, `pin_spotlight_event`, `trigger_sync`) and URI resources (`prevue://events/today`, `prevue://events/weekend`, `prevue://venues/directory`).
* Scoped Agent Client Protocol (ACP) bidirectional control protocol for automated multi-agent orchestration.

### 7. Retro Mode & Spotify Audio Stream Architecture
* Scoped 16-color/256-color EGA/VGA dithering matrix shaders and low-resolution composite video rasterizers.
* Scoped Spotify Web Playback SDK integration in Settings with user playlist selection, autoplay on dashboard boot, and default fallback to curated public 90s weather channel jazz and synthwave.

### 8. Automated Verification
* 24 passing tests in pytest across circuit breaker states, all provider adapters, JSON-LD parsing, iCal streams, ticket commitment toggles, scheduler lifecycle, and REST endpoints.
* Zero error TypeScript compilation and Vite frontend production bundle.
