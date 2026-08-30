# Release v0.14.0: Expanded 15-Market Regional Presets Matrix

## Overview
Release v0.14.0 expands OpenPrevue's regional market presets across 15 major North American and international metro hubs, unifying 1-click channel provisioning between the First-Boot Setup Wizard and the Location Settings control center.

## Key Deliverables

### 1. Expanded 15-Market Preset Matrix (`regionalPresets.ts`)
* **New Markets Added:** Atlanta (30303), Portland (97201), Miami (33101), Orlando (32801), Tampa (33602), San Francisco (94102), Las Vegas (89101), New Orleans (70112), and Dallas (75201).
* **Existing Baseline Markets:** New York City (10001), Los Angeles (90012), Chicago (60601), Austin (78701), Seattle (98101), and London (EC1A 1BB).
* **Unified Coordinates & Radial Radius:** Each preset maps exact municipal coordinates, default radial search distances, and postal codes.

### 2. Dual-UI Integration (`SetupModal.vue` & `SettingsView.vue`)
* **Setup Wizard Grid:** Expanded responsive 15-market preset button grid on initial boot.
* **Settings Control Center:** Direct 1-click market switching in the Location & Discovery tab.

### 3. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite frontend production bundle.
