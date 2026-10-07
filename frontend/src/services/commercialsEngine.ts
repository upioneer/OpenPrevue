/** 
 * Retro 1990s Television Commercial and Station Bumper Playback Engine for OpenPrevue.
 * Manages periodic video commercial interruption intervals, server dropzone synchronization,
 * YouTube 90s commercial playlist integration, and audio ducking.
 */

import { ref } from "vue";
import { audioSynth } from "./audioSynth";
import { deleteCommercialClipFile, fetchCommercialClips, updateSetting, uploadCommercialClipFile } from "../api/client";

export interface CommercialClip {
  id: string;
  name: string;
  url: string;
  filename?: string;
  sizeBytes?: number;
  durationSeconds?: number;
  isUserUploaded?: boolean;
  type?: 'local' | 'youtube';
}

class CommercialsEngine {
  public isEnabled = ref<boolean>(false);
  public frequencyPerHour = ref<number>(4); // 1 - 10 per hour (default: 4)
  public isPlayingCommercial = ref<boolean>(false);
  public currentClip = ref<CommercialClip | null>(null);
  public clips = ref<CommercialClip[]>([]);
  public dropzoneDirectory = ref<string>("./data/commercials");
  public commercialSource = ref<'youtube' | 'local' | 'combined'>('youtube');
  public youtubeSourceUrl = ref<string>('https://www.youtube.com/playlist?list=PLQ82R4ElALew');
  private timer: ReturnType<typeof setInterval> | null = null;
  private lastIntervalMs: number | null = null;
  private timeoutTimer: ReturnType<typeof setTimeout> | null = null;
  private wasAudioPlayingBeforeVideo: boolean = false;

  constructor() {
    this.loadSettings();
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

      const source = localStorage.getItem("openprevue_commercials_source");
      if (source === "youtube" || source === "local" || source === "combined") {
        this.commercialSource.value = source;
      }
    } catch {
      // Use defaults
    }
  }

  private saveSettings(): void {
    try {
      localStorage.setItem("openprevue_commercials_enabled", this.isEnabled.value ? "1" : "0");
      localStorage.setItem("openprevue_commercials_frequency", this.frequencyPerHour.value.toString());
      localStorage.setItem("openprevue_commercials_source", this.commercialSource.value);
    } catch {
      // Ignored
    }
  }

  public async syncWithServerDropzone(): Promise<void> {
    try {
      const res = await fetchCommercialClips();
      if (res.dropzone_directory) {
        this.dropzoneDirectory.value = res.dropzone_directory;
      }
      if (res.clips) {
        const serverClips: CommercialClip[] = res.clips.map(c => ({
          id: c.id,
          name: c.name,
          filename: c.filename,
          sizeBytes: c.size_bytes,
          url: c.url,
          isUserUploaded: true,
          type: "local",
        }));
        this.clips.value = serverClips;
      }
    } catch {
      // Keep defaults if offline/server error
    }
  }

  public updateConfig(enabled: boolean, frequencyPerHour: number, source?: 'youtube' | 'local' | 'combined'): void {
    this.isEnabled.value = enabled;
    this.frequencyPerHour.value = Math.max(1, Math.min(10, frequencyPerHour));
    if (source) {
      this.commercialSource.value = source;
    }
    this.saveSettings();
    this.restartTimer();
  }

  public updateSettingsFromSystem(settings: any): void {
    if (!settings) return;
    if (settings.commercials_enabled !== undefined) {
      this.isEnabled.value = settings.commercials_enabled === "1";
    }
    if (settings.commercials_frequency_per_hour !== undefined) {
      const parsedFreq = parseInt(settings.commercials_frequency_per_hour, 10);
      if (!isNaN(parsedFreq)) {
        this.frequencyPerHour.value = Math.max(1, Math.min(10, parsedFreq));
      }
    }
    if (settings.commercials_source && ["youtube", "local", "combined"].includes(settings.commercials_source)) {
      this.commercialSource.value = settings.commercials_source as 'youtube' | 'local' | 'combined';
    }
    if (settings.youtube_source_url) {
      this.youtubeSourceUrl.value = settings.youtube_source_url;
    }
    this.saveSettings();
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
      type: "local",
    };
    this.clips.value.push(clip);
    return clip;
  }

  public async removeClip(id: string, filename?: string): Promise<void> {
    const target = this.clips.value.find(c => c.id === id);
    this.clips.value = this.clips.value.filter(c => c.id !== id);
    const fname = filename || target?.filename || target?.name;
    if (fname && target?.isUserUploaded) {
      try {
        await deleteCommercialClipFile(fname);
      } catch {
        // Fallback silently if offline or already removed
      }
    }
  }

  public playRandomCommercial(): void {
    if (this.isPlayingCommercial.value) return;

    const sourceMode = this.commercialSource.value;
    const hasLocalClips = this.clips.value.length > 0;

    if (sourceMode === "youtube" || (!hasLocalClips && sourceMode === "local")) {
      this.playYouTubeCommercial();
    } else if (sourceMode === "local" && hasLocalClips) {
      const randomIndex = Math.floor(Math.random() * this.clips.value.length);
      this.playClip(this.clips.value[randomIndex]);
    } else if (sourceMode === "combined") {
      if (hasLocalClips && Math.random() < 0.5) {
        const randomIndex = Math.floor(Math.random() * this.clips.value.length);
        this.playClip(this.clips.value[randomIndex]);
      } else {
        this.playYouTubeCommercial();
      }
    } else {
      this.playYouTubeCommercial();
    }
  }

  public playYouTubeCommercial(): void {
    const clip: CommercialClip = {
      id: "yt_commercial_" + Date.now(),
      name: "Curated 1990s Television Commercial",
      url: this.youtubeSourceUrl.value || "https://www.youtube.com/playlist?list=PLQ82R4ElALew",
      durationSeconds: 60,
      isUserUploaded: false,
      type: "youtube",
    };
    this.playClip(clip);
  }

  public playClip(clip: CommercialClip): void {
    this.currentClip.value = clip;
    this.isPlayingCommercial.value = true;

    // Safety fallback timeout, armed FIRST: if anything below throws or the
    // clip never reports back, the break still concludes after 90 seconds.
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
    }
    this.timeoutTimer = setTimeout(() => {
      if (this.isPlayingCommercial.value) {
        this.onCommercialFinished();
      }
    }, 90000);

    // Heartbeat so any operator screen can prove breaks are airing.
    updateSetting("last_commercial_break", new Date().toISOString()).catch(() => {});

    // Duck / Pause background audio during commercial break
    const audioState = audioSynth.getPlaybackState();
    this.wasAudioPlayingBeforeVideo = audioState.isAudioActive || audioState.isAudioStreamPlaying;
    if (this.wasAudioPlayingBeforeVideo) {
      audioSynth.pauseAudioStream();
      audioSynth.stopTapeHiss();
    }
  }

  public onCommercialFinished(): void {
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
      this.timeoutTimer = null;
    }
    this.isPlayingCommercial.value = false;
    this.currentClip.value = null;

    // Resume background audio if it was playing before
    if (this.wasAudioPlayingBeforeVideo) {
      audioSynth.playAudioStream();
      audioSynth.startTapeHiss();
    }
  }

  public startTimer(): void {
    this.restartTimer();
  }

  public restartTimer(): void {
    if (!this.isEnabled.value) {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
      this.lastIntervalMs = null;
      return;
    }

    // Frequency: 1 - 10 per hour
    // e.g., 4 per hour = every 900 seconds (15 minutes)
    const intervalMs = Math.round((3600 / this.frequencyPerHour.value) * 1000);

    // The dashboard re-arms this on every 60s refresh and every settings
    // broadcast. Recreating the interval each time would reset the countdown
    // faster than it can ever elapse (shortest cadence is 6 minutes), so
    // scheduled breaks would never fire. Only recreate when the cadence
    // actually changed.
    if (this.timer && this.lastIntervalMs === intervalMs) return;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.lastIntervalMs = intervalMs;
    this.timer = setInterval(() => {
      this.playRandomCommercial();
    }, intervalMs);
  }

  public stopTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.lastIntervalMs = null;
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
      this.timeoutTimer = null;
    }
  }
}

export const commercialsEngine = new CommercialsEngine();
