# Release v0.16.1: Turnkey Audio OOBE, Dynamic Spotify Metadata, Sports Team Logos & Colors, 3 Grid Presentation Scales, Content-Quantized Row Snapping, Chunky 1990s TV Typography, Sustained EAS Attention Siren, High-Res QR Pass, Strict Geo-Filtering, 9-Tab Settings & Local Ollama AI

## Overview
Release v0.16.1 introduces 3 selectable channel schedule presentation density modes (4 Rows Classic TV, 7 Rows Balanced, 12 Rows Dense), content-quantized row-snapping pause cadence (preventing cut-off rows during scroll holds), chunky 1990s television broadcast typography calibrated for 1080p displays, maximized sports matchup logo cards with franchise colors and CDN vector artwork, sample-accurate sustained 8-to-10 second Emergency Alert System (EAS) dual-tone siren synthesis, dynamic Spotify metadata resolution via the official Spotify oEmbed API, persistent background audio with a floating mini-dock, high-contrast QR code passes engineered for CRT scanline resistance, geographic radius enforcement across all event listings, automatic city and ZIP code geocoding resolution, self-hosted Ollama local AI heartbeat testing, a reorganized 9-tab Settings Control Center, a calibrated 30 px/sec broadcast scroll speed, and backend filesystem dropzone synchronization for video commercials (`./data/commercials/`).

## Key Deliverables

### 1. 3 Channel Schedule Presentation Scales & Density Modes (`TimelineGrid.vue`, `DashboardView.vue`, `SettingsView.vue`, `seeder.py`, `types/index.ts`)
* **Classic TV (4 Rows - True-to-Scale 1990s Broadcast):** Authentic 1:1 reproduction of the 1990s Prevue Channel on an NTSC CRT TV. Features generous row heights, large chunky broadcast typography (`text-base sm:text-lg md:text-xl font-black`), large team badges, roomy time slots, and maximum vintage immersion.
* **Balanced (7 Rows - Happy Medium):** The optimal compromise between retro broadcast scale and information visibility, rendering 7 comfortable rows with clear typography.
* **Dense (12 Rows - High-Density Overview):** Information-dense mode displaying up to 12 simultaneous channels on screen for command-center monitoring.
* **Multi-Orientation & Resolution Adaptation:** Seamlessly adapts across 1080p, 4K, portrait displays (61% grid height), and Raspberry Pi touchscreens.
* **Interactive Settings Selector:** Configurable in Settings Tab 2 with interactive visual preset cards.

### 2. Content-Quantized Row Snapping & Clean Pause Engine (`TimelineGrid.vue`)
* **Clean Boundary Row Snapping:** Replaced arbitrary time-based stop points with a content-quantized row-snapping algorithm. When scrolling between batches, the grid calculates the exact pixel offset of the next channel row (`targetEl.offsetTop`) and snaps precisely to the top border, guaranteeing zero half-cut or severed rows during reading pauses.
* **Dynamic Viewport Fit:** Dynamically calculates how many whole channel rows fit within the active screen height, ensuring clean framing on 1080p monitors, 4K TVs, and Raspberry Pi touchscreens alike.
* **Customizable Cadence Controls:** Configurable in Settings Tab 2 (`scroll_pause_duration` from 0s to 10s, and `scroll_page_interval` from 3s to 15s).

### 3. Sustained EAS Dual-Tone Attention Siren Synthesis (`audioSynth.ts`, `EASBanner.vue`, `eas.py`)
* **Sample-Accurate Web Audio Scheduling:** Integrated `playEASSiren()` into the singleton `audioSynth` engine using sample-accurate Web Audio oscillator scheduling (`setValueAtTime`, `linearRampToValueAtTime`, `stop(now + duration)`).
* **Eliminated Premature Cut-Offs:** Resolved asynchronous timer race conditions where temporary audio contexts were prematurely closed, ensuring the full sustained **8 to 10 second** dual-tone attention siren (853 Hz + 960 Hz) plays without interruption.
* **Direct Control:** Added a `[ MUTE SIREN ]` action button and seamless alert dismissal.

### 4. Chunky 1990s Television Typography & Maximized Spotlight Logos (`SpotlightPane.vue`, `TimelineGrid.vue`, `HeaderBar.vue`, `DividerRibbon.vue`, `main.css`)
* **Authentic 1990s TV Typography Scale:** Replaced modern high-density web font sizes with bold, chunky television-standard typography (`16px` root baseline, `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-2xl`, `text-3xl`), eliminating the "too high-def" look on 1080p monitors while preserving retro CRT character.
* **Maximized Team Logo Real Estate:** Expanded the left spotlight preview column to `48%` and scaled sports team circular badge containers to **`w-24` through `w-40`** with thick franchise-colored borders, glowing halos, and prominent `VS` broadcast graphics.
* **Schedule Grid Sports Badges:** Integrated franchise color pills, league badges (`[NBA]`, `[NFL]`, `[MLB]`), and team abbreviations into the scrolling schedule grid rows.

### 5. Sports Team Branding, Franchise Colors & CDN Logos (`sportsTheme.ts`, `SpotlightPane.vue`)
* **Authentic Team Matchup Cards:** Created a dedicated sports branding engine resolving team names across major leagues (NBA, NFL, MLB, MLS, NHL, Formula 1, NASCAR) to official primary/secondary colors, acronyms, and high-res vector logos.
* **Robust Matchup Parser:** Added case-insensitive title parsing (`/\s+(?:vs\.?|against|v)\s+/i` and `/\s+@\s+/i`) that extracts team pairs and league prefixes reliably across all uppercase/lowercase formats.
* **Graceful High-Contrast Fallback:** Seamless fallback to calculated team abbreviation badges styled in the franchise's exact hex color scheme if offline.

### 6. Dynamic Spotify Metadata Resolution & Persistent Audio Player (`spotify.py`, `SpotifyPlayerModal.vue`, `HeaderBar.vue`, `DividerRibbon.vue`, `SpotlightPane.vue`, `App.vue`)
* **Dynamic Metadata Resolution:** Added `GET /api/v1/spotify/metadata` to dynamically resolve playlist titles and authors directly from Spotify's official oEmbed API without hardcoded strings.
* **Persistent Background Playback:** Permanently mounted the Spotify player iframe in the application DOM via CSS visibility, preventing audio from cutting out when minimizing the player, closing the dialog, or navigating pages.
* **Floating Mini-Dock:** Minimized player docks cleanly to the bottom-right corner with animated equalizer bars, live playlist title, and 1-click `[ EXPAND ]` and `[ X ]` controls.
* **1-Click Accessible Buttons:** Added prominent `[ SPOTIFY ]` and `[ PLAY SPOTIFY ]` buttons across the Header Bar, Divider Ribbon, and Spotlight Ticker ribbon.

### 7. High-Res Level H Scannable QR Code Pass (`SpotlightPane.vue`)
* **CRT Scanline-Resistant QR Code:** Enlarged QR code display with High (Level H, 30% error recovery) correction to ensure instant camera scanning even through dense phosphor scanlines and CRT curvature.
* **Click-to-Expand Mobile Pass Modal:** Clicking the QR code pass opens a high-resolution full-screen modal with direct mobile box office link.

### 8. Geographic Radius Enforcement & Location-Anchored Ingestion (`events.py`, `mock.py`, `sports.py`, `ticketing.py`, `settings.py`)
* **Strict Geographic Proximity Filtering:** Updated `GET /api/v1/events` to calculate haversine distance against the active system coordinates and filter out any listings beyond the configured radius, completely preventing cross-city data pollution.
* **Dynamic Location-Anchored Providers:** Updated `mock`, `sports_leagues`, and `secondary_ticketing` providers to dynamically generate and filter fixtures matching the user's active geographic coordinates.
* **Automatic Re-Sync on Location Update:** Modifying latitude, longitude, postal code, or radius in settings immediately re-syncs listings and refreshes live weather.

### 9. Instant City & Postal Code Geocoding Resolution (`geocoding.py`, `weather.py`, `SetupModal.vue`, `SettingsView.vue`)
* **Live Geocoding Pipeline:** Added `/api/v1/weather/geocode` resolving city names (e.g., *Austin*, *Chicago*, *London*) and US ZIP codes (e.g., *78701*, *60601*, *90210*) to exact latitude, longitude, and formatted metro broadcast labels.
* **Instant Auto-Resolution:** Both the Setup Wizard and Settings Control Center resolve typed locations on Enter, blur, or clicking `[ RESOLVE ]`.

### 10. Default Channel Schedule Scan Speed Calibration (30 px/sec)
* **30 px/sec Broadcast Speed:** Enforced default listings autoscroll scan speed to 30 px/sec across backend database seeders, unit test isolation, and frontend views for optimal CRT legibility.

### 11. Local AI Engine Support & Self-Hosted Ollama Heartbeat (`ai.py`, `client.ts`, `SettingsView.vue`)
* **Ollama Endpoint:** Added `POST /api/v1/ai/ollama/ping` to test round-trip latency and enumerate installed local models.
* **Interactive Settings Control:** Settings Tab 5 features base URL input, model dropdown, and an interactive `[ TEST OLLAMA HEARTBEAT & CONNECTION ]` diagnostic probe.

### 12. Settings Control Center Reorganization (`SettingsView.vue`)
* **9 Dedicated Tabs:** Split settings into distinct, numbered tabs for instant discovery (`[ 1. LOCATION & DISCOVERY ]`, `[ 2. DISPLAY & SCAN SPEED ]`, `[ 3. SPOTIFY & VINTAGE AUDIO ]`, `[ 4. RETRO COMMERCIALS ]`, `[ 5. TICKET INGESTION & AI ]`, `[ 6. TELEGRAM & SPEECH ]`, `[ 7. EMERGENCY ALERTS (EAS) ]`, `[ 8. PROVIDER CREDENTIALS ]`, `[ 9. SYSTEM & UPDATES ]`).

### 13. Step-by-Step Telegram Bot Setup Guide (`SettingsView.vue`, `README.md`)
* Integrated 5-step visual guide detailing how to create a bot with `@BotFather`, copy the HTTP API token, paste into OpenPrevue, generate a pairing code, and link devices.

### 14. Commercials Filesystem Dropzone & Video API (`commercials.py`)
* Automatically detects and serves video clips placed in `./data/commercials/` on the server or Docker host.
* Added `GET /api/v1/commercials`, `POST /api/v1/commercials/upload`, and `GET /api/v1/commercials/stream/{filename}`.

### 15. Automated Verification
* 65/65 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite production build.
