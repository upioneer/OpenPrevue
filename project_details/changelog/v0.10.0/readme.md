# Release v0.10.0: Retro CRT Shaders, Analog Audio Synthesizer & Ticket Ingestion Hub

## Overview
Release v0.10.0 brings authentic 1990s CRT video emulation with selectable color palettes (EGA 16, VGA 256, C64, Amber, Green), resolution downsampling rasterizers (320x240, 480x360), Web Audio analog tape hiss and 60 Hz cassette hum generators, and a dedicated multi-format ticket ingestion hub supporting iCalendar (.ics), MIME email (.eml), and Microsoft Outlook (.msg) messages.

## Key Deliverables

### 1. Retro CRT Shader & Palette Engine (`retroShader.ts`)
* **Selectable Vintage Palettes:** Instant live switching between Standard Prevue Blue, EGA 16-color PC, Commodore 64, Amber monochrome, and Green phosphor terminal modes.
* **Scanline & Phosphor Bloom Control:** Real-time scanline density slider and phosphor text glow bloom.
* **Resolution Downsampler:** Optional pixelated downsampling scaling containers (320x240, 480x360, 640x480, Native).
* **CRT Curvature & Vignette:** Barrel screen distortion mimicking vintage cathode ray tube monitors.

### 2. Web Audio Analog Tape Hiss & Muzak Streamer (`audioSynth.ts`)
* **Analog Tape Hiss Synthesizer:** Real-time pink/brown noise generator with bandpass tape head filtering and subtle 60 Hz transformer mains hum.
* **Ambient Stream Player:** Curated 90s weather channel smooth jazz and vaporwave background streams.
* **Divider Ribbon Media Bar:** Persistent play/pause toggle with animated retro audio equalizer bars (`|||`).

### 3. Ticket Ingestion Hub & Enhanced AI Extractor (`SettingsView.vue`)
* **Multi-Format Drag & Drop Zone:** Ingests calendar files (.ics / RFC 5545), email messages (.eml / RFC 822), and Outlook messages (.msg).
* **Graceful Ingestion Guard:** Resilient validation and error handling for encrypted, unsupported, or corrupted message files.
* **Enhanced AI Ticket Extractor Section:** Optional configuration fields for Groq, OpenAI, and Anthropic API keys to parse irregular indie venue flyers and unformatted promoter receipts, while deterministic parsing handles standard vendor receipts out of the box.

### 4. Automated Verification
* 50 passing unit and integration tests in pytest.
* Zero error TypeScript type checking and Vite frontend production compilation.
