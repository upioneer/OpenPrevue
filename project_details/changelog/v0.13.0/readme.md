# Release v0.13.0: First-Boot Setup Wizard, NYC Privacy Defaults & Multi-Arch GHCR Docker CI/CD

## Overview
Release v0.13.0 introduces an interactive First-Boot Setup Wizard modal for instant local channel configuration, sanitizes default container environment variables to New York City for privacy, and integrates automated multi-architecture Docker container builds (linux/amd64, linux/arm64) publishing to GitHub Container Registry (ghcr.io).

## Key Deliverables

### 1. Interactive First-Boot Setup Wizard (`SetupModal.vue`)
* **First-Run Modal Dialog:** Automatically prompts users on first startup to pick their local broadcasting market or type custom coordinates.
* **Instant City Presets:** Quick 1-click selection for New York City, Los Angeles, Chicago, Austin, Seattle, and London.
* **Instant Channel Provisioning:** Automatically updates SQLite settings and triggers an immediate initial provider synchronization pass for the chosen region.

### 2. Default Privacy & Environment Sanitization
* **New York City Baseline:** Default container timezone set to America/New_York (ZIP 10001, Lat 40.7128, Lon -74.0060, Radius 25 miles).
* **Updated Mock Venues:** Realistic mock event inventory updated with iconic New York venues (Madison Square Garden, Radio City Music Hall, Brooklyn Steel, Beacon Theatre, Gershwin Theatre, Blue Note Jazz Club, Comedy Cellar).

### 3. Multi-Architecture GitHub Actions Docker Pipeline (`ci.yml`)
* **Cross-Platform Compilation:** Automated QEMU + Buildx compilation for both `linux/amd64` (standard servers/desktops) and `linux/arm64` (Raspberry Pi 4/5, Apple Silicon, ARM SBCs).
* **GitHub Container Registry (GHCR):** Automated publishing to `ghcr.io/upioneer/openprevue` with Semantic Version tags (`:0.13.0`, `:0.13`, `:latest`, `:sha-xxx`).
* **GitHub Actions Layer Caching (`type=gha`):** Rapid incremental build caching.

### 4. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite frontend production bundle.
