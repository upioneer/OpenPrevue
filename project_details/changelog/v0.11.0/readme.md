# Release v0.11.0: Vertical Portrait & Small Display Responsive Optimization

## Overview
Release v0.11.0 introduces responsive portrait layout adaptations and small touchscreen optimizations tailored for vertical monitor kiosks (9:16 / 1080x1920) and Raspberry Pi homelab touchscreens (480x320, 800x480, 1024x600).

## Key Deliverables

### 1. Vertical Portrait Layout Engine (`DashboardView.vue`)
* **Dynamic Proportions:** Automatically activates in vertical orientation (`@media (orientation: portrait)` or `@media (max-aspect-ratio: 1/1)`).
* **Expanded Schedule Height:** Timeline Grid expands from 49% to 61% of vertical viewport height, displaying 12 to 16 rows of upcoming venue events simultaneously.
* **Optimized Spotlight Height:** Spotlight Pane adapts from 45% to 34% height to maximize the visible TV guide grid.

### 2. Small Display & Raspberry Pi Touchscreen Optimization (`SpotlightPane.vue`, `TimelineGrid.vue`)
* **Adaptive Typography:** Fluid font scaling ensuring venue names and showtimes remain readable on compact 3.5-inch to 7-inch displays.
* **Responsive QR Code:** Scales between 36px and 56px to preserve vertical space without losing optical mobile scannability.
* **Touch Friendly Action Targets:** All ticket commitment toggles (`[+TKT]`, `[TICKET]`) and audio buttons maintain touch target dimensions for finger navigation on capacitive and resistive Pi touchscreens.

### 3. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite frontend production bundle.
