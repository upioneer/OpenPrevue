/** Web Audio analog tape hiss generator, RF headend filter, and ambient muzak player service. */

export type AudioFilterProfile = "bypass" | "rf_12khz" | "crt_mono" | "vhs_headend" | "cassette";

export interface AudioFilterConfig {
  enabled: boolean;
  profile: AudioFilterProfile;
  cutoffHz: number; // 8000 - 16000 Hz (default: 12000)
  cutGainDb: number; // -18 to 0 dB (default: -8)
}

class AnalogAudioService {
  private audioCtx: AudioContext | null = null;
  private hissGain: GainNode | null = null;
  private humGain: GainNode | null = null;
  private masterGain: GainNode | null = null;
  private noiseNode: AudioNode | null = null;
  private humOsc: OscillatorNode | null = null;
  private isTapeHissPlaying: boolean = false;
  private audioElement: HTMLAudioElement | null = null;
  private mediaSourceNode: MediaElementAudioSourceNode | null = null;
  private isMuzakPlaying: boolean = false;

  // DSP Filter Chain Nodes
  private highPassFilter: BiquadFilterNode | null = null;
  private peakingFilter: BiquadFilterNode | null = null;
  private highShelfFilter: BiquadFilterNode | null = null;
  private lowPassFilter: BiquadFilterNode | null = null;

  private filterConfig: AudioFilterConfig = {
    enabled: true,
    profile: "rf_12khz",
    cutoffHz: 12000,
    cutGainDb: -8,
  };

  // Curated 90s Weather Channel, Vaporwave, Smooth Jazz, and Official Spotify Playlist
  private defaultStreams = [
    { name: "90s Weather Channel Jazz", url: "https://stream.zeno.fm/4wt00p9zsz4tv" },
    { name: "Prevue Vintage Muzak FM", url: "https://stream.zeno.fm/752y841vyb8uv" },
    { name: "Smooth Jazz 24/7", url: "https://streaming.exclusive.radio/er/smoothjazz/icecast.audio" },
  ];

  public readonly officialSpotifyPlaylist = {
    title: "OpenPrevue Vintage Muzak & Cable Headend Jazz",
    url: "https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f",
    embedUrl: "https://open.spotify.com/embed/playlist/3jiPmIT4RugR8TPhli5Obk?utm_source=generator&theme=0",
  };

  constructor() {
    this.loadFilterConfig();
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

  public initAudioContext(): void {
    if (!this.audioCtx) {
      const AudioContextClass =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.audioCtx = new AudioContextClass();
      this.masterGain = this.audioCtx.createGain();
      this.masterGain.connect(this.audioCtx.destination);

      this.initFilterNodes();
    }

    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  private initFilterNodes(): void {
    if (!this.audioCtx || !this.masterGain) return;

    this.highPassFilter = this.audioCtx.createBiquadFilter();
    this.peakingFilter = this.audioCtx.createBiquadFilter();
    this.highShelfFilter = this.audioCtx.createBiquadFilter();
    this.lowPassFilter = this.audioCtx.createBiquadFilter();

    // Chain: HP -> Peak -> HighShelf -> LowPass -> MasterGain
    this.highPassFilter.connect(this.peakingFilter);
    this.peakingFilter.connect(this.highShelfFilter);
    this.highShelfFilter.connect(this.lowPassFilter);
    this.lowPassFilter.connect(this.masterGain);

    this.applyFilterParameters();
  }

  public getFilterConfig(): AudioFilterConfig {
    return { ...this.filterConfig };
  }

  public updateFilterConfig(newConfig: Partial<AudioFilterConfig>): void {
    this.filterConfig = { ...this.filterConfig, ...newConfig };
    this.applyFilterParameters();
    this.saveFilterConfig();
  }

  public setFilterProfile(profile: AudioFilterProfile): void {
    this.filterConfig.profile = profile;
    if (profile === "bypass") {
      this.filterConfig.enabled = false;
    } else {
      this.filterConfig.enabled = true;
      if (profile === "rf_12khz") {
        this.filterConfig.cutoffHz = 12000;
        this.filterConfig.cutGainDb = -8;
      } else if (profile === "crt_mono") {
        this.filterConfig.cutoffHz = 10000;
        this.filterConfig.cutGainDb = -12;
      } else if (profile === "vhs_headend") {
        this.filterConfig.cutoffHz = 11500;
        this.filterConfig.cutGainDb = -10;
      } else if (profile === "cassette") {
        this.filterConfig.cutoffHz = 8500;
        this.filterConfig.cutGainDb = -9;
      }
    }
    this.applyFilterParameters();
    this.saveFilterConfig();
  }

  private applyFilterParameters(): void {
    if (!this.audioCtx || !this.highShelfFilter || !this.lowPassFilter || !this.highPassFilter || !this.peakingFilter) {
      return;
    }

    const t = this.audioCtx.currentTime;

    if (!this.filterConfig.enabled || this.filterConfig.profile === "bypass") {
      // Flat / Transparent Bypass
      this.highPassFilter.type = "highpass";
      this.highPassFilter.frequency.setValueAtTime(10, t);
      this.peakingFilter.type = "peaking";
      this.peakingFilter.gain.setValueAtTime(0, t);
      this.highShelfFilter.type = "highshelf";
      this.highShelfFilter.frequency.setValueAtTime(12000, t);
      this.highShelfFilter.gain.setValueAtTime(0, t);
      this.lowPassFilter.type = "lowpass";
      this.lowPassFilter.frequency.setValueAtTime(22000, t);
      return;
    }

    const profile = this.filterConfig.profile;
    const cutoff = this.filterConfig.cutoffHz || 12000;
    const cutGain = this.filterConfig.cutGainDb || -8;

    if (profile === "rf_12khz") {
      // 1990s Composite / RF Baseband (12 kHz High-Shelf Cut)
      this.highPassFilter.type = "highpass";
      this.highPassFilter.frequency.setValueAtTime(20, t);
      this.peakingFilter.type = "peaking";
      this.peakingFilter.frequency.setValueAtTime(3200, t);
      this.peakingFilter.gain.setValueAtTime(1.0, t);
      this.highShelfFilter.type = "highshelf";
      this.highShelfFilter.frequency.setValueAtTime(cutoff, t);
      this.highShelfFilter.gain.setValueAtTime(cutGain, t);
      this.lowPassFilter.type = "lowpass";
      this.lowPassFilter.frequency.setValueAtTime(15000, t);
    } else if (profile === "crt_mono") {
      // CRT TV Internal 3" Speaker Simulation
      this.highPassFilter.type = "highpass";
      this.highPassFilter.frequency.setValueAtTime(280, t);
      this.peakingFilter.type = "peaking";
      this.peakingFilter.frequency.setValueAtTime(2400, t);
      this.peakingFilter.gain.setValueAtTime(3.5, t);
      this.highShelfFilter.type = "highshelf";
      this.highShelfFilter.frequency.setValueAtTime(cutoff, t);
      this.highShelfFilter.gain.setValueAtTime(cutGain, t);
      this.lowPassFilter.type = "lowpass";
      this.lowPassFilter.frequency.setValueAtTime(9500, t);
    } else if (profile === "vhs_headend") {
      // Cable Headend Modulator with NTSC 15.734 kHz subcarrier notch
      this.highPassFilter.type = "highpass";
      this.highPassFilter.frequency.setValueAtTime(45, t);
      this.peakingFilter.type = "notch";
      this.peakingFilter.frequency.setValueAtTime(15734, t);
      this.peakingFilter.Q.setValueAtTime(10, t);
      this.highShelfFilter.type = "highshelf";
      this.highShelfFilter.frequency.setValueAtTime(cutoff, t);
      this.highShelfFilter.gain.setValueAtTime(cutGain, t);
      this.lowPassFilter.type = "lowpass";
      this.lowPassFilter.frequency.setValueAtTime(13500, t);
    } else if (profile === "cassette") {
      // Analog Type I Cassette Tape
      this.highPassFilter.type = "highpass";
      this.highPassFilter.frequency.setValueAtTime(30, t);
      this.peakingFilter.type = "peaking";
      this.peakingFilter.frequency.setValueAtTime(120, t);
      this.peakingFilter.gain.setValueAtTime(3.0, t);
      this.highShelfFilter.type = "highshelf";
      this.highShelfFilter.frequency.setValueAtTime(cutoff, t);
      this.highShelfFilter.gain.setValueAtTime(cutGain, t);
      this.lowPassFilter.type = "lowpass";
      this.lowPassFilter.frequency.setValueAtTime(11000, t);
    }
  }

  public setTapeHissVolume(volumePercent: number): void {
    if (this.hissGain && this.audioCtx) {
      const vol = Math.max(0, Math.min(1, volumePercent / 100)) * 0.15;
      this.hissGain.gain.setValueAtTime(vol, this.audioCtx.currentTime);
    }
    if (this.humGain && this.audioCtx) {
      const vol = Math.max(0, Math.min(1, volumePercent / 100)) * 0.04;
      this.humGain.gain.setValueAtTime(vol, this.audioCtx.currentTime);
    }
  }

  public startTapeHiss(volumePercent: number = 30): void {
    this.initAudioContext();
    if (!this.audioCtx || !this.masterGain || this.isTapeHissPlaying) return;

    // Generate 5 seconds of pink noise buffer
    const bufferSize = this.audioCtx.sampleRate * 5;
    const noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
    const output = noiseBuffer.getChannelData(0);

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

    // Filter noise to simulate vintage magnetic tape head response
    const filter = this.audioCtx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.value = 1800;
    filter.Q.value = 0.7;

    this.hissGain = this.audioCtx.createGain();
    const hissVol = Math.max(0, Math.min(1, volumePercent / 100)) * 0.15;
    this.hissGain.gain.setValueAtTime(hissVol, this.audioCtx.currentTime);

    whiteNoise.connect(filter);
    filter.connect(this.hissGain);
    this.hissGain.connect(this.masterGain);
    whiteNoise.start(0);
    this.noiseNode = whiteNoise;

    // Add 60Hz CRT transformer mains hum
    this.humOsc = this.audioCtx.createOscillator();
    this.humOsc.type = "sine";
    this.humOsc.frequency.setValueAtTime(60, this.audioCtx.currentTime);

    this.humGain = this.audioCtx.createGain();
    const humVol = Math.max(0, Math.min(1, volumePercent / 100)) * 0.04;
    this.humGain.gain.setValueAtTime(humVol, this.audioCtx.currentTime);

    this.humOsc.connect(this.humGain);
    this.humGain.connect(this.masterGain);
    this.humOsc.start();

    this.isTapeHissPlaying = true;
  }

  public stopTapeHiss(): void {
    if (this.noiseNode) {
      try {
        (this.noiseNode as AudioBufferSourceNode).stop();
        this.noiseNode.disconnect();
      } catch (e) {
        // Ignored
      }
      this.noiseNode = null;
    }

    if (this.humOsc) {
      try {
        this.humOsc.stop();
        this.humOsc.disconnect();
      } catch (e) {
        // Ignored
      }
      this.humOsc = null;
    }

    this.isTapeHissPlaying = false;
  }

  public playMuzakStream(streamUrl?: string, volumePercent: number = 50): void {
    this.initAudioContext();

    if (!this.audioElement) {
      this.audioElement = new Audio();
      this.audioElement.crossOrigin = "anonymous";

      // Connect media element to Web Audio DSP filter chain
      if (this.audioCtx && this.highPassFilter && !this.mediaSourceNode) {
        try {
          this.mediaSourceNode = this.audioCtx.createMediaElementSource(this.audioElement);
          this.mediaSourceNode.connect(this.highPassFilter);
        } catch (e) {
          console.warn("MediaElementAudioSource direct connect fallback:", e);
        }
      }
    }

    const url = streamUrl || this.defaultStreams[0].url;
    if (this.audioElement.src !== url) {
      this.audioElement.src = url;
    }

    this.audioElement.volume = Math.max(0, Math.min(1, volumePercent / 100));
    this.audioElement
      .play()
      .then(() => {
        this.isMuzakPlaying = true;
      })
      .catch(() => {
        this.isMuzakPlaying = false;
      });
  }

  public playLocalAudioFile(file: File, volumePercent: number = 50): void {
    this.initAudioContext();

    if (!this.audioElement) {
      this.audioElement = new Audio();
      this.audioElement.crossOrigin = "anonymous";

      if (this.audioCtx && this.highPassFilter && !this.mediaSourceNode) {
        try {
          this.mediaSourceNode = this.audioCtx.createMediaElementSource(this.audioElement);
          this.mediaSourceNode.connect(this.highPassFilter);
        } catch (e) {
          console.warn("MediaElementAudioSource direct connect fallback:", e);
        }
      }
    }

    const blobUrl = URL.createObjectURL(file);
    this.audioElement.src = blobUrl;
    this.audioElement.volume = Math.max(0, Math.min(1, volumePercent / 100));
    this.audioElement
      .play()
      .then(() => {
        this.isMuzakPlaying = true;
      })
      .catch(() => {
        this.isMuzakPlaying = false;
      });
  }

  public pauseMuzak(): void {
    if (this.audioElement) {
      this.audioElement.pause();
      this.isMuzakPlaying = false;
    }
  }

  public toggleMuzak(volumePercent: number = 50): boolean {
    if (this.isMuzakPlaying) {
      this.pauseMuzak();
      return false;
    } else {
      this.playMuzakStream(undefined, volumePercent);
      return true;
    }
  }

  public setMuzakVolume(volumePercent: number): void {
    if (this.audioElement) {
      this.audioElement.volume = Math.max(0, Math.min(1, volumePercent / 100));
    }
  }

  public getPlaybackState() {
    return {
      isTapeHissPlaying: this.isTapeHissPlaying,
      isMuzakPlaying: this.isMuzakPlaying,
      streams: this.defaultStreams,
      filter: this.filterConfig,
      officialSpotifyPlaylist: this.officialSpotifyPlaylist,
    };
  }
}

export const audioSynth = new AnalogAudioService();
