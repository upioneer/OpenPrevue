# Release v0.9.0: Sports Leagues & Secondary Ticketing Matrix

## Overview
Release v0.9.0 expands the OpenPrevue ingestion matrix with native sports and motorsports league aggregators (Formula 1, NASCAR, IndyCar, MotoGP, NFL, NBA, MLB, MLS) and primary/secondary ticketing connectors (Live Nation, Vivid Seats, StubHub, TripAdvisor / Viator).

## Key Deliverables

### 1. Sports & Motorsports League Feeds (`providers/sports.py`)
* **Motorsport Series Calendars:**
  * **Formula 1 (F1):** United States Grand Prix (COTA) and Miami Grand Prix schedules and session links.
  * **NASCAR Cup Series:** Superspeedway pack racing and short track fixtures (Talladega 500).
  * **NTT IndyCar Series:** Road courses and oval events (Barber Indy Grand Prix).
  * **MotoGP World Championship:** Grand Prix of the Americas premier motorcycle fixtures.
* **Major American Sports Leagues:**
  * **NFL:** New Orleans Saints and regional football matchups with ticket pricing brackets.
  * **NBA:** New Orleans Pelicans and arena basketball schedules.
  * **MLB:** Major League Baseball series fixtures.
  * **MLS:** Major League Soccer regular season matches.

### 2. Secondary Marketplaces & Promoter Connectors (`providers/ticketing.py`)
* **Live Nation Promoter Tours:** Direct concert headline tour dates and verified ticket links.
* **Vivid Seats Resale Feed:** Secondary ticket market listings and festival weekend passes with buyer guarantee data.
* **StubHub Marketplace:** Secondary concert and sporting event tickets with FanProtect pricing.
* **TripAdvisor / Viator Experiences:** Municipal riverboat cruises, jazz tours, and culinary experiences.

### 3. Ingestion Engine & Deduplication Fusion
* Canonical venue deduplication mapping stadiums, raceways, music halls, and river wharves without database fragmentation.
* Automatic price fusion preserving lowest minimum and highest maximum price boundaries across primary and secondary marketplaces.

### 4. Automated Verification
* 50 passing tests in pytest across all 8 provider adapters, MCP JSON-RPC handlers, EAS pipelines, speech intent routers, and WebSocket managers.
* Zero error TypeScript compilation and Vite frontend production bundle.
