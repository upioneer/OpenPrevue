/** 
 * Web Audio analog tape hiss generator, 12 kHz RF headend filter, 
 * EAS Dual-Tone Siren Synthesizer, and Spotify audio management service for OpenPrevue.
 */

import { ref } from "vue";

export type AudioFilterProfile = "bypass" | "rf_12khz" | "crt_mono" | "vhs_headend" | "cassette";

export interface AudioFilterConfig {
  enabled: boolean;
  profile: AudioFilterProfile;
  cutoffHz: number; // 8000 - 16000 Hz (default: 12000)
  cutGainDb: number; // -18 to 0 dB (default: -8)
}

class AnalogAudioService {
  public isAudioActive = ref<boolean>(false);
  public isTapeHissPlaying = ref<boolean>(false);
  public isAutoPlayOptedIn = ref<boolean>(true);
  public isEASSirenPlaying = ref<boolean>(false);

  // Backward-compatible aliases
  public get isMuzakPlaying() {
    return this.isAudioActive.value;
  }
  public get isAudioStreamPlaying() {
    return this.isAudioActive.value;
  }

  private audioCtx: AudioContext | null = null;
  private hissGain: GainNode | null = null;
  private humGain: GainNode | null = null;
  private masterGain: GainNode | null = null;
  private noiseNode: AudioNode | null = null;
  private humOsc: OscillatorNode | null = null;
  private hasInstalledAutoPlayListener: boolean = false;

  // DSP Filter Chain Nodes
  private highPassFilter: BiquadFilterNode | null = null;
  private peakingFilter: BiquadFilterNode | null = null;
  private highShelfFilter: BiquadFilterNode | null = null;
  private lowPassFilter: BiquadFilterNode | null = null;

  // EAS Dual-Tone Attention Signal Nodes (853 Hz + 960 Hz)
  private easOsc1: OscillatorNode | null = null;
  private easOsc2: OscillatorNode | null = null;
  private easGain: GainNode | null = null;
  private easTimeout: ReturnType<typeof setTimeout> | null = null;

  private filterConfig: AudioFilterConfig = {
    enabled: true,
    profile: "rf_12khz",
    cutoffHz: 12000,
    cutGainDb: -8,
  };

  // Official Curated Spotify Playlist for OpenPrevue (The User's Vision)
  public readonly officialSpotifyPlaylist = {
    title: '"OpenPrevue" by upioneer',
    url: "https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f",
    embedUrl: "https://open.spotify.com/embed/playlist/3jiPmIT4RugR8TPhli5Obk?utm_source=generator&theme=0",
  };

  constructor() {
    this.loadFilterConfig();
    this.loadAudioPreferences();
  }

  public getPlaybackState() {
    return {
      isAudioActive: this.isAudioActive.value,
      isTapeHissPlaying: this.isTapeHissPlaying.value,
      isAudioStreamPlaying: this.isAudioActive.value,
      isMuzakPlaying: this.isAudioActive.value,
    };
  }

  public pauseAudioStream(): void {
    if (this.isTapeHissPlaying.value) {
      this.stopTapeHiss();
    }
  }

  public playAudioStream(): void {
    if (this.isAudioActive.value) {
      this.startTapeHiss(35);
    }
  }

  private loadFilterConfig(): void {
    try {
      const saved = localStorage.getItem("openprevue_audio_filter_config");
      if (saved) {
        this.filterConfig = { ...this.filterConfig, ...JSON.parse(saved) };
      }
    } catch {
      // Use defaults
    }
  }

  private saveFilterConfig(): void {
    try {
      localStorage.setItem("openprevue_audio_filter_config", JSON.stringify(this.filterConfig));
    } catch {
      // Ignore
    }
  }

  private loadAudioPreferences(): void {
    try {
      const optIn = localStorage.getItem("openprevue_audio_autoplay");
      if (optIn !== null) {
        this.isAutoPlayOptedIn.value = optIn === "1";
      }
    } catch {
      // Use default true
    }
  }

  public setAutoPlayOptIn(enabled: boolean): void {
    this.isAutoPlayOptedIn.value = enabled;
    try {
      localStorage.setItem("openprevue_audio_autoplay", enabled ? "1" : "0");
    } catch {
      // Ignored
    }
  }

  public initAutoPlayTrigger(): void {
    if (typeof window === "undefined" || this.hasInstalledAutoPlayListener) return;
    this.hasInstalledAutoPlayListener = true;

    const tryAutoStart = () => {
      if (this.isAutoPlayOptedIn.value && !this.isAudioActive.value) {
        this.startTurnkeyAudio();
      }
      window.removeEventListener("click", tryAutoStart);
      window.removeEventListener("keydown", tryAutoStart);
      window.removeEventListener("touchstart", tryAutoStart);
    };

    window.addEventListener("click", tryAutoStart, { once: true, passive: true });
    window.addEventListener("keydown", tryAutoStart, { once: true, passive: true });
    window.addEventListener("touchstart", tryAutoStart, { once: true, passive: true });
  }

  public startTurnkeyAudio(): void {
    this.startTapeHiss(35);
    this.isAudioActive.value = true;
  }

  public toggleMasterAudio(): boolean {
    if (this.isAudioActive.value || this.isTapeHissPlaying.value) {
      this.stopTapeHiss();
      this.isAudioActive.value = false;
      return false;
    } else {
      this.startTurnkeyAudio();
      return true;
    }
  }

  private initAudioContext(): void {
    if (!this.audioCtx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      this.audioCtx = new AudioCtx();

      // Build 4-Stage Analog DSP Filter Chain
      this.highPassFilter = this.audioCtx.createBiquadFilter();
      this.peakingFilter = this.audioCtx.createBiquadFilter();
      this.highShelfFilter = this.audioCtx.createBiquadFilter();
      this.lowPassFilter = this.audioCtx.createBiquadFilter();
      this.masterGain = this.audioCtx.createGain();

      // Serial filter chain
      this.highPassFilter.connect(this.peakingFilter);
      this.peakingFilter.connect(this.highShelfFilter);
      this.highShelfFilter.connect(this.lowPassFilter);
      this.lowPassFilter.connect(this.masterGain);
      this.masterGain.connect(this.audioCtx.destination);

      this.applyFilterParameters();
    }

    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  public updateFilterConfig(config: Partial<AudioFilterConfig>): void {
    this.filterConfig = { ...this.filterConfig, ...config };
    this.saveFilterConfig();
    this.applyFilterParameters();
  }

  public setFilterProfile(profile: AudioFilterProfile): void {
    this.filterConfig.profile = profile;
    if (profile === "rf_12khz") {
      this.filterConfig.cutoffHz = 12000;
      this.filterConfig.cutGainDb = -8;
    } else if (profile === "crt_mono") {
      this.filterConfig.cutoffHz = 9500;
      this.filterConfig.cutGainDb = -12;
    } else if (profile === "vhs_headend") {
      this.filterConfig.cutoffHz = 11500;
      this.filterConfig.cutGainDb = -10;
    } else if (profile === "cassette") {
      this.filterConfig.cutoffHz = 10000;
      this.filterConfig.cutGainDb = -6;
    }
    this.saveFilterConfig();
    this.applyFilterParameters();
  }

  public getFilterConfig(): AudioFilterConfig {
    return { ...this.filterConfig };
  }

  private applyFilterParameters(): void {
    if (!this.audioCtx || !this.highPassFilter || !this.peakingFilter || !this.highShelfFilter || !this.lowPassFilter) {
      return;
    }

    const t = this.audioCtx.currentTime;

    if (!this.filterConfig.enabled || this.filterConfig.profile === "bypass") {
      this.highPassFilter.type = "allpass";
      this.peakingFilter.type = "allpass";
      this.highShelfFilter.type = "allpass";
      this.lowPassFilter.type = "allpass";
      return;
    }

    // 1. High Pass filter: Gently cut sub-bass rumble below 40 Hz
    this.highPassFilter.type = "highpass";
    this.highPassFilter.frequency.setValueAtTime(40, t);
    this.highPassFilter.Q.setValueAtTime(0.7, t);

    // 2. Peaking filter: Mild CRT mid-range broadcast presence at 2.5 kHz
    this.peakingFilter.type = "peaking";
    this.peakingFilter.frequency.setValueAtTime(2500, t);
    this.peakingFilter.Q.setValueAtTime(1.2, t);
    this.peakingFilter.gain.setValueAtTime(1.5, t);

    // 3. High Shelf filter: Analog tape / RF attenuation
    this.highShelfFilter.type = "highshelf";
    this.highShelfFilter.frequency.setValueAtTime(this.filterConfig.cutoffHz, t);
    this.highShelfFilter.gain.setValueAtTime(this.filterConfig.cutGainDb, t);

    // 4. Low Pass filter: Hard brickwall cutoff above 14 kHz for authentic 1990s RF headend
    this.lowPassFilter.type = "lowpass";
    this.lowPassFilter.frequency.setValueAtTime(14000, t);
    this.lowPassFilter.Q.setValueAtTime(0.8, t);
  }

  public startTapeHiss(volumePercent: number = 35): void {
    if (typeof window === "undefined") return;
    this.initAudioContext();
    if (!this.audioCtx || !this.highPassFilter) return;

    if (this.isTapeHissPlaying.value) {
      this.setTapeHissVolume(volumePercent);
      return;
    }

    try {
      const bufferSize = 2 * this.audioCtx.sampleRate;
      const noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
      const output = noiseBuffer.getChannelData(0);

      // Generate authentic 1/f Pink Noise with soft analog roll-off
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.05;
        b6 = white * 0.115926;
      }

      const whiteNoise = this.audioCtx.createBufferSource();
      whiteNoise.buffer = noiseBuffer;
      whiteNoise.loop = true;

      this.hissGain = this.audioCtx.createGain();
      const gainVal = Math.max(0, Math.min(1, (volumePercent / 100) * 0.08));
      this.hissGain.gain.setValueAtTime(gainVal, this.audioCtx.currentTime);

      // 60 Hz NTSC Mains Ground Hum
      this.humOsc = this.audioCtx.createOscillator();
      this.humOsc.type = "sine";
      this.humOsc.frequency.setValueAtTime(60, this.audioCtx.currentTime);

      this.humGain = this.audioCtx.createGain();
      const humVal = Math.max(0, Math.min(1, (volumePercent / 100) * 0.012));
      this.humGain.gain.setValueAtTime(humVal, this.audioCtx.currentTime);

      // Route through DSP filter chain
      whiteNoise.connect(this.hissGain);
      this.hissGain.connect(this.highPassFilter);

      this.humOsc.connect(this.humGain);
      this.humGain.connect(this.highPassFilter);

      whiteNoise.start(0);
      this.humOsc.start(0);

      this.noiseNode = whiteNoise;
      this.isTapeHissPlaying.value = true;
    } catch (err) {
      console.debug("Web Audio Start Error:", err);
    }
  }

  public setTapeHissVolume(volumePercent: number): void {
    if (!this.audioCtx) return;
    const t = this.audioCtx.currentTime;
    if (this.hissGain) {
      const gainVal = Math.max(0, Math.min(1, (volumePercent / 100) * 0.08));
      this.hissGain.gain.linearRampToValueAtTime(gainVal, t + 0.1);
    }
    if (this.humGain) {
      const humVal = Math.max(0, Math.min(1, (volumePercent / 100) * 0.012));
      this.humGain.gain.linearRampToValueAtTime(humVal, t + 0.1);
    }
  }

  public stopTapeHiss(): void {
    if (!this.isTapeHissPlaying.value) return;

    if (this.audioCtx && this.hissGain && this.humGain) {
      const t = this.audioCtx.currentTime;
      this.hissGain.gain.linearRampToValueAtTime(0.0001, t + 0.3);
      this.humGain.gain.linearRampToValueAtTime(0.0001, t + 0.3);

      setTimeout(() => {
        try {
          if (this.noiseNode) {
            (this.noiseNode as AudioBufferSourceNode).stop();
            this.noiseNode.disconnect();
            this.noiseNode = null;
          }
          if (this.humOsc) {
            this.humOsc.stop();
            this.humOsc.disconnect();
            this.humOsc = null;
          }
        } catch {
          // Ignored
        }
        this.isTapeHissPlaying.value = false;
      }, 350);
    } else {
      this.isTapeHissPlaying.value = false;
    }
  }

  /**
   * Play the authentic sustained Emergency Alert System (EAS) dual-tone attention siren (853 Hz + 960 Hz).
   * Web Audio graph scheduled with sample accuracy to prevent race conditions or premature cut-offs.
   */
  public playEASSiren(durationSeconds: number = 8): void {
    this.stopEASSiren();

    try {
      this.initAudioContext();
      if (!this.audioCtx) return;

      if (this.audioCtx.state === "suspended") {
        this.audioCtx.resume();
      }

      const now = this.audioCtx.currentTime;
      const safeDuration = Math.max(2, durationSeconds);

      // 853 Hz oscillator (Lower EBS dual-tone)
      this.easOsc1 = this.audioCtx.createOscillator();
      this.easOsc1.type = "sine";
      this.easOsc1.frequency.setValueAtTime(853, now);

      // 960 Hz oscillator (Upper EBS dual-tone)
      this.easOsc2 = this.audioCtx.createOscillator();
      this.easOsc2.type = "sine";
      this.easOsc2.frequency.setValueAtTime(960, now);

      // Master siren gain with clean envelope: instant attack, sustained hold, smooth decay
      this.easGain = this.audioCtx.createGain();
      this.easGain.gain.setValueAtTime(0.0001, now);
      this.easGain.gain.linearRampToValueAtTime(0.35, now + 0.05);
      this.easGain.gain.setValueAtTime(0.35, now + safeDuration - 0.1);
      this.easGain.gain.linearRampToValueAtTime(0.0001, now + safeDuration);

      this.easOsc1.connect(this.easGain);
      this.easOsc2.connect(this.easGain);
      this.easGain.connect(this.audioCtx.destination);

      this.easOsc1.start(now);
      this.easOsc2.start(now);
      this.easOsc1.stop(now + safeDuration);
      this.easOsc2.stop(now + safeDuration);

      this.isEASSirenPlaying.value = true;

      this.easTimeout = setTimeout(() => {
        this.isEASSirenPlaying.value = false;
      }, (safeDuration + 0.1) * 1000);
    } catch (err) {
      console.debug("EAS Siren synthesis error:", err);
      this.isEASSirenPlaying.value = false;
    }
  }

  /**
   * Immediately mute/stop any active EAS attention siren.
   */
  public stopEASSiren(): void {
    if (this.easTimeout) {
      clearTimeout(this.easTimeout);
      this.easTimeout = null;
    }

    if (this.easGain && this.audioCtx) {
      try {
        const now = this.audioCtx.currentTime;
        this.easGain.gain.cancelScheduledValues(now);
        this.easGain.gain.linearRampToValueAtTime(0.0001, now + 0.05);
      } catch {
        // Ignored
      }
    }

    const osc1 = this.easOsc1;
    const osc2 = this.easOsc2;
    const gain = this.easGain;

    this.easOsc1 = null;
    this.easOsc2 = null;
    this.easGain = null;
    this.isEASSirenPlaying.value = false;

    setTimeout(() => {
      try {
        if (osc1) {
          osc1.stop();
          osc1.disconnect();
        }
        if (osc2) {
          osc2.stop();
          osc2.disconnect();
        }
        if (gain) {
          gain.disconnect();
        }
      } catch {
        // Cleaned
      }
    }, 60);
  }
}

export const audioSynth = new AnalogAudioService();
