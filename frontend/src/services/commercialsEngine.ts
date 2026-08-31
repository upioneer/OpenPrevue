/** 
 * Retro 1990s Television Commercial and Station Bumper Playback Engine for OpenPrevue.
 * Manages periodic video commercial interruption intervals, server dropzone synchronization, and audio ducking.
 */

import { ref } from "vue";
import { audioSynth } from "./audioSynth";
import { fetchCommercialClips, uploadCommercialClipFile } from "../api/client";

export interface CommercialClip {
  id: string;
  name: string;
  url: string;
  filename?: string;
  sizeBytes?: number;
  durationSeconds?: number;
  isUserUploaded?: boolean;
}

class CommercialsEngine {
  public isEnabled = ref<boolean>(false);
  public frequencyPerHour = ref<number>(4); // 1 - 10 per hour (default: 4)
  public isPlayingCommercial = ref<boolean>(false);
  public currentClip = ref<CommercialClip | null>(null);
  public clips = ref<CommercialClip[]>([]);
  public dropzoneDirectory = ref<string>("./data/commercials");
  private timer: ReturnType<typeof setInterval> | null = null;
  private wasAudioPlayingBeforeVideo: boolean = false;

  constructor() {
    this.loadSettings();
    this.initDefaultClips();
    this.syncWithServerDropzone();
  }

  private loadSettings(): void {
    try {
      const enabled = localStorage.getItem("openprevue_commercials_enabled");
      if (enabled !== null) {
        this.isEnabled.value = enabled === "1";
      }

      const freq = localStorage.getItem("openprevue_commercials_frequency");
      if (freq) {
        this.frequencyPerHour.value = Math.max(1, Math.min(10, parseInt(freq, 10)));
      }
    } catch {
      // Use defaults
    }
  }

  private saveSettings(): void {
    try {
      localStorage.setItem("openprevue_commercials_enabled", this.isEnabled.value ? "1" : "0");
      localStorage.setItem("openprevue_commercials_frequency", this.frequencyPerHour.value.toString());
    } catch {
      // Ignored
    }
  }

  private initDefaultClips(): void {
    // Initial OEM placeholder slot / retro simulated station ID clips
    this.clips.value = [
      {
        id: "oem_bumper_1",
        name: "OpenPrevue 1995 Station ID Bumper",
        url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        durationSeconds: 15,
        isUserUploaded: false,
      }
    ];
  }

  public async syncWithServerDropzone(): Promise<void> {
    try {
      const res = await fetchCommercialClips();
      if (res.dropzone_directory) {
        this.dropzoneDirectory.value = res.dropzone_directory;
      }
      if (res.clips && res.clips.length > 0) {
        const serverClips: CommercialClip[] = res.clips.map(c => ({
          id: c.id,
          name: c.name,
          filename: c.filename,
          sizeBytes: c.size_bytes,
          url: c.url,
          isUserUploaded: true,
        }));
        this.clips.value = serverClips;
      }
    } catch {
      // Keep defaults if offline/server error
    }
  }

  public updateConfig(enabled: boolean, frequencyPerHour: number): void {
    this.isEnabled.value = enabled;
    this.frequencyPerHour.value = Math.max(1, Math.min(10, frequencyPerHour));
    this.saveSettings();
    this.restartTimer();
  }

  public async uploadClipToServer(file: File): Promise<CommercialClip> {
    const res = await uploadCommercialClipFile(file);
    const clip: CommercialClip = {
      id: res.clip.id,
      name: res.clip.name,
      filename: res.clip.filename,
      sizeBytes: res.clip.size_bytes,
      url: res.clip.url,
      isUserUploaded: true,
    };
    this.clips.value.push(clip);
    return clip;
  }

  public removeClip(id: string): void {
    this.clips.value = this.clips.value.filter(c => c.id !== id);
  }

  public playRandomCommercial(): void {
    if (this.clips.value.length === 0 || this.isPlayingCommercial.value) return;

    const randomIndex = Math.floor(Math.random() * this.clips.value.length);
    const clip = this.clips.value[randomIndex];
    this.playClip(clip);
  }

  public playClip(clip: CommercialClip): void {
    this.currentClip.value = clip;
    this.isPlayingCommercial.value = true;

    // Duck / Pause background audio
    const audioState = audioSynth.getPlaybackState();
    this.wasAudioPlayingBeforeVideo = audioState.isAudioActive || audioState.isAudioStreamPlaying;
    if (this.wasAudioPlayingBeforeVideo) {
      audioSynth.pauseAudioStream();
    }
  }

  public onCommercialFinished(): void {
    this.isPlayingCommercial.value = false;
    this.currentClip.value = null;

    // Resume background audio if it was playing before
    if (this.wasAudioPlayingBeforeVideo) {
      audioSynth.playAudioStream();
    }
  }

  public startTimer(): void {
    this.restartTimer();
  }

  public restartTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }

    if (!this.isEnabled.value) return;

    // Frequency: 1 - 10 per hour
    // e.g., 4 per hour = every 900 seconds (15 minutes)
    const intervalMs = Math.round((3600 / this.frequencyPerHour.value) * 1000);
    this.timer = setInterval(() => {
      this.playRandomCommercial();
    }, intervalMs);
  }

  public stopTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }
}

export const commercialsEngine = new CommercialsEngine();
