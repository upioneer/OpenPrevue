# Release v0.14.1: Softened Retro CRT Scanlines & Visual Polish

## Overview
Release v0.14.1 softens the default CRT scanline raster effect from an aggressive 45% opacity down to a subtle 12%, preserving the nostalgic 1990s cathode-ray texture while improving legibility across text headers and timeline schedule listings.

## Key Deliverables

### 1. Subtle Scanline Texture (`main.css` & `retroShader.ts`)
* **Toned Down Default Intensity:** Lowered baseline `--scanline-opacity` from `0.45` to `0.12` (12%).
* **Refined Raster Geometry:** Adjusted vertical gradient repeat pattern to 4px spacing with soft opacity blending.
* **Readable Typography:** Ensures neon yellow event titles, showtimes, and ticket commitment tags remain readable on all monitor types without eye fatigue.

### 2. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite frontend production bundle.
