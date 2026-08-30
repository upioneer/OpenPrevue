# Release v0.12.0: Dynamic Vector Sports Matchup Graphics & Team Logos

## Overview
Release v0.12.0 introduces an integrated vector sports crest registry and dynamic matchup graphic generator in the Spotlight Pane, replacing generic placeholder imagery with crisp, offline-cached team logos (NFL, NBA, MLB, MLS, F1, NASCAR, IndyCar, MotoGP).

## Key Deliverables

### 1. Vector Team Crest & League Registry (`sportsAssets.ts`)
* **Built-in Offline SVG Assets:** Lightweight, high-contrast vector logos for major sports franchises (New Orleans Saints, Atlanta Falcons, New Orleans Pelicans, Los Angeles Lakers, Golden State Warriors, Houston Astros, Texas Rangers, Houston Dynamo, Austin FC) and motorsport series badges (Formula 1, NASCAR, IndyCar, MotoGP).
* **Matchup Parser Engine (`parseSportsMatchup`):** Automatically extracts home and away teams, tournament league headers, and primary team brand colors from event titles.

### 2. Retro Broadcast Matchup Graphic in Spotlight Pane (`SpotlightPane.vue`)
* **Split Team Display:** Away team crest on left and Home team crest on right with authentic 90s yellow "VS" center badge.
* **League Banner:** Monospaced top league indicator (e.g. `[ NFL ON PREVUE ]`, `[ FORMULA 1 ON PREVUE ]`, `[ NBA MATCHUP ]`).
* **Matchup Label:** Full team names and matchup marquee at the bottom of the media card.

### 3. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite frontend production bundle.
