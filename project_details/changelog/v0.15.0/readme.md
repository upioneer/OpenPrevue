# Release v0.15.0: 1990s RF / Composite Baseband Audio Filter & Headend Encoding

## Overview
Release v0.15.0 introduces an authentic 1990s Web Audio DSP filtering pipeline for Muzak, local audio tracks, and streaming playback, replicating the bandwidth-limited RF modulator frequency roll-off and composite baseband acoustics of vintage cable headends.

## Key Deliverables

### 1. Web Audio DSP Filtering Pipeline (`audioSynth.ts`)
* **12 kHz High-Shelf Cut Filter:** Applies a configurable high-shelf attenuation curve centered at 12 kHz (default -8 dB) to soften harsh modern treble and simulate 1990s composite video baseband audio.
* **Acoustic Filter Profiles:**
  * `rf_12khz`: 1990s Composite / RF Baseband (12 kHz High-Shelf Cut, -8 dB).
  * `crt_mono`: 1990s CRT TV Internal 3-Inch Speaker (280 Hz High-Pass + 10 kHz Low-Pass + 2.4 kHz Peaking).
  * `vhs_headend`: Cable Headend Modulator (11.5 kHz High-Shelf + 15.734 kHz NTSC subcarrier notch filter).
  * `cassette`: Vintage Cassette Tape (120 Hz Warm Bass Boost + 8.5 kHz High-Cut).
  * `bypass`: Hi-Fi Transparent Bypass (unfiltered full spectrum).
* **Fine-Tuning Controls:** Interactive sliders for high-shelf cutoff frequency (8 kHz to 16 kHz) and cut gain (-18 dB to 0 dB).

### 2. Headend Audio Encoding & Ingestion Dropzone (`SettingsView.vue`)
* **Encoding Specifications:** Guidance for homelab setups to encode audio to 128 to 192 kbps MP3 or 16-bit 44.1 kHz WAV/OGG.
* **Local File Audio Player:** Drag-and-drop ingestion for `.mp3`, `.wav`, `.ogg`, and `.flac` files, routed directly through the active 12 kHz DSP filter.

### 3. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite production bundle.
