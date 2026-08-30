# Release v0.4.0: Telegram Bot Service & Remote Curation

## Overview
Release v0.4.0 delivers the complete OpenPrevue Telegram Bot Service, enabling remote mobile queries, real time TV spotlight curation, keyword alert tracking, and automated push notifications via outbound long polling without requiring open router ports or inbound webhooks.

## Key Deliverables

### 1. Asynchronous Telegram Bot Worker
* **Outbound Long Polling (`getUpdates`):** Connects asynchronously directly to Telegram API with zero inbound port forwarding or reverse proxy exposure.
* **Device Pairing Wizard (`/pair PREVUE-XXXX`):** Secure authentication flow linking Telegram accounts to the local SQLite database using 6-character ephemeral pairing tokens generated via the web UI.

### 2. Full Command Suite & Remote Curation
* `/today`: Displays monospaced bulletin of events scheduled for today.
* `/tonight`: Filtered schedule of evening events starting after 5:00 PM local time.
* `/weekend`: Curated Friday through Sunday weekend digest.
* `/search <query>`: Fast search querying artist, team, or venue name.
* `/pin <event_id>`: Pins an event to the 45% spotlight rotation on TV displays and broadcasts live WebSocket update.
* `/unpin <event_id>`: Removes an event from spotlight rotation.
* `/watch <keyword>`: Registers a keyword for push alerts.
* `/unwatch <keyword>`: Removes a keyword from push alerts.
* `/watchlist`: Lists active monitored keywords.
* `/status`: Displays system uptime, total cached listings, metro label, and current weather.
* `/help`: Complete monospaced command directory and syntax guide.

### 3. Boxed Interaction Guard & Retro ASCII Formatting
* **Unknown Command Catch-All:** Intercepts unrecognized commands with an informational error card directing users to valid commands.
* **Parameter Syntax Validation:** Missing or invalid arguments immediately return formatted usage examples (e.g., `ERROR: Missing search query.` followed by `USAGE: /search Preservation Hall`).
* **Unpaired User Guard:** Intercepts unauthenticated chats with pairing instructions.
* **Authentic 90s ASCII Cards:** Formatted using fixed-width monospaced box characters (`+---+`, `|`) matching the cable channel guide aesthetic.

### 4. Background Watchlist Scanning & Push Notifications
* Ingestion pipeline automatically scans incoming raw event titles and descriptions against active user watchlists, dispatching immediate notification cards to paired Telegram accounts upon new matches.
* Scheduled weekend digest push service sending curated listings to all paired users.

### 5. Management REST API Endpoints
* `POST /api/v1/telegram/pair-code`: Generates new pairing codes for device onboarding.
* `GET /api/v1/telegram/status`: Returns bot worker configuration and active status.
* `GET /api/v1/telegram/users`: Lists paired Telegram users.
* `DELETE /api/v1/telegram/users/{chat_id}`: Deactivates and unpairs accounts.
* `POST /api/v1/telegram/test-message`: Dispatches test notification card to verify delivery.

### 6. Automated Verification
* 36 passing tests in pytest covering message formatters, REST endpoints, command routing, and error guards.
* Zero error TypeScript compilation and Vite frontend production bundle.
