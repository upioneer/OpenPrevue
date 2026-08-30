# Release v0.7.0: Emergency Alert System (EAS) & Public Safety Ingestion

## Overview
Release v0.7.0 introduces the Emergency Alert System (EAS) and public safety ingestion module, featuring real-time warnings from NOAA / National Weather Service (NWS), USGS seismic hazards, high-visibility retro top toast banners, and authentic 1990s dual-tone audio attention signals.

## Key Deliverables

### 1. EAS Multi-Source Ingestion Engine (`eas.py`)
* **NOAA / NWS CAP Feed:** Continuous ingestion of active meteorological warnings (Tornado Warnings, Severe Thunderstorms, Flash Floods, Hurricane Watches) anchored to configured coordinates.
* **USGS Earthquake Hazards Ingestion:** Radial seismic event monitoring for earthquakes exceeding magnitude 3.5.
* **IPAWS Civil Emergency Messages:** Civil danger, evacuation, active shooter, and AMBER alerts.
* **Automated 5-Minute Polling:** Integrated recurring background trigger in APScheduler (`recurring_eas_poll`).

### 2. High-Visibility Retro Toast Banner (`EASBanner.vue`)
* **Flashing Monospaced Top Overlay:** High-contrast retro styling (`#AA0000` / `#FFFF00`) displaying issuing authority, affected parish/county zones, and emergency instructions.
* **Configurable Auto-Dismiss Progress Bar:** Visual countdown timer respecting user duration settings (10 to 120 seconds) with manual `[ DISMISS ]` button.
* **Web Audio Attention Signal:** Client-side synthesizer playing the authentic 1990s dual-tone EAS attention signal (853 Hz + 960 Hz dual sine wave tones).

### 3. Settings Control Center Integration
* **Dedicated EAS Tab:**
  * Master EAS toggle (`eas_enabled`).
  * Minimum severity filter (`All`, `Moderate`, `Severe`, `Extreme`).
  * Toast banner display duration slider (10 to 120s).
  * Dual-tone audio chime toggle (`eas_sound_enabled`).
  * 1-click "Dispatch Simulated EAS Alert" broadcast simulator for visual and audio verification.

### 4. Automated Verification
* 43 passing tests in pytest across EAS alert creation, REST endpoints, spoken intent parsing, and provider adapters.
* Zero error TypeScript compilation and Vite frontend production bundle.
