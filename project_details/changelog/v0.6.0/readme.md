# Release v0.6.0: Telegram Voice Notes & Hybrid Speech Pipeline

## Overview
Release v0.6.0 introduces bidirectional voice note interactions to the OpenPrevue Telegram bot, featuring turnkey offline speech processing, natural spoken intent routing, and optional cloud acceleration via Groq Whisper and ElevenLabs.

## Key Deliverables

### 1. Telegram Voice Message Listener
* **Voice Note Ingestion:** Intercepts incoming `.ogg` Opus audio memos via `filters.VOICE` and `filters.AUDIO`.
* **Spoken Intent Router:** Translates spoken English queries into deterministic bot commands:
  * "What is happening tonight?" -> `/tonight`
  * "Show me the weekend schedule" -> `/weekend`
  * "What concerts are today?" -> `/today`
  * "Check system status and weather" -> `/status`
  * "Search Preservation Hall Jazz" -> `/search Preservation Hall`
  * "Track New Orleans Saints" -> `/watch Saints`
  * "Pin event mock-123" -> `/pin mock-123`

### 2. Hybrid Speech Pipeline
* **Turnkey Offline Mode (Default):** Zero-config offline operation running directly in Docker with local intent extraction and 90s TV announcer synthesizer audio generation.
* **Enhanced Cloud Mode (Optional):** Automatic routing through Groq Whisper large-v3 for accelerated transcription (< 80ms) and ElevenLabs for neural voice synthesis when API keys are configured in Settings.
* **Automatic Fallback:** Seamlessly reverts to local processing if external API keys or networks are unavailable.

### 3. Audio Synthesis & Voice Reply
* Turnkey PCM WAV audio generator producing valid audio buffers for audio replies and test previews.
* Automated voice delivery over Telegram using `reply_voice`.

### 4. Automated Verification
* 41 passing tests in pytest across spoken intent parsing, turnkey audio synthesis, speech diagnostics, and Telegram message formatters.
* Zero error TypeScript compilation and Vite frontend production bundle.
