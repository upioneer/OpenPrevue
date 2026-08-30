/** Web Audio analog tape hiss generator and ambient muzak player service. */

class AnalogAudioService {
  private audioCtx: AudioContext | null = null;
  private hissGain: GainNode | null = null;
  private humGain: GainNode | null = null;
  private masterGain: GainNode | null = null;
  private noiseNode: AudioNode | null = null;
  private humOsc: OscillatorNode | null = null;
  private isTapeHissPlaying: boolean = false;
  private audioElement: HTMLAudioElement | null = null;
  private isMuzakPlaying: boolean = false;

  // Curated 90s Weather Channel & Vaporwave ambient jazz streams
  private defaultStreams = [
    { name: "90s Weather Channel Jazz", url: "https://stream.zeno.fm/4wt00p9zsz4tv" },
    { name: "Prevue Vintage Muzak FM", url: "https://stream.zeno.fm/752y841vyb8uv" },
    { name: "Smooth Jazz 24/7", url: "https://streaming.exclusive.radio/er/smoothjazz/icecast.audio" }
  ];

  public initAudioContext(): void {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.audioCtx = new AudioContextClass();
      this.masterGain = this.audioCtx.createGain();
      this.masterGain.connect(this.audioCtx.destination);
    }

    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }
  }

  public setTapeHissVolume(volumePercent: number): void {
    if (this.hissGain && this.audioCtx) {
      const vol = Math.max(0, Math.min(1, volumePercent / 100)) * 0.15; // capped for subtle ambient warmth
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
    filter.frequency.value = 1800; // Hz
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
    if (!this.audioElement) {
      this.audioElement = new Audio();
      this.audioElement.crossOrigin = "anonymous";
    }

    const url = streamUrl || this.defaultStreams[0].url;
    if (this.audioElement.src !== url) {
      this.audioElement.src = url;
    }

    this.audioElement.volume = Math.max(0, Math.min(1, volumePercent / 100));
    this.audioElement.play().then(() => {
      this.isMuzakPlaying = true;
    }).catch(() => {
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
    };
  }
}

export const audioSynth = new AnalogAudioService();
