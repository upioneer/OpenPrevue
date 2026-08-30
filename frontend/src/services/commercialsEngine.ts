/** 
 * Retro 1990s Television Commercial and Station Bumper Playback Engine for OpenPrevue.
 * Manages periodic video commercial interruption intervals, user video dropzones, and audio ducking.
 */

import { ref } from "vue";
import { audioSynth } from "./audioSynth";

export interface CommercialClip {
  id: string;
  name: string;
  url: string;
  durationSeconds?: number;
  isUserUploaded?: boolean;
}

class CommercialsEngine {
  public isEnabled = ref<boolean>(false);
  public frequencyPerHour = ref<number>(4); // 1 - 10 per hour (default: 4)
  public isPlayingCommercial = ref<boolean>(false);
  public currentClip = ref<CommercialClip | null>(null);
  public clips = ref<CommercialClip[]>([]);
  private timer: ReturnType<typeof setInterval> | null = null;
  private wasMuzakPlayingBeforeVideo: boolean = false;

  constructor() {
    this.loadSettings();
    this.initDefaultClips();
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

  public updateConfig(enabled: boolean, frequencyPerHour: number): void {
    this.isEnabled.value = enabled;
    this.frequencyPerHour.value = Math.max(1, Math.min(10, frequencyPerHour));
    this.saveSettings();
    this.restartTimer();
  }

  public addUploadedClip(file: File): CommercialClip {
    const objectUrl = URL.createObjectURL(file);
    const clip: CommercialClip = {
      id: `user_${Date.now()}`,
      name: file.name,
      url: objectUrl,
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

    // Duck / Pause background Muzak
    const audioState = audioSynth.getPlaybackState();
    this.wasMuzakPlayingBeforeVideo = audioState.isMuzakPlaying;
    if (this.wasMuzakPlayingBeforeVideo) {
      audioSynth.pauseMuzak();
    }
  }

  public onCommercialFinished(): void {
    this.isPlayingCommercial.value = false;
    this.currentClip.value = null;

    // Resume background audio if it was playing before
    if (this.wasMuzakPlayingBeforeVideo) {
      audioSynth.playMuzakStream();
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
