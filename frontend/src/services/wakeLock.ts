/**
 * Screen Wake Lock API service for OpenPrevue kiosks and wall displays.
 * Prevents mobile devices, tablets, and smart TVs from sleeping while displaying the schedule.
 */

import { ref } from "vue";

class ScreenWakeLockService {
  public isSupported = ref<boolean>(typeof navigator !== "undefined" && "wakeLock" in navigator);
  public isWakeLockActive = ref<boolean>(false);
  private wakeLockSentinel: any = null;
  private isUserOptedIn: boolean = true;

  constructor() {
    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible" && this.isUserOptedIn && !this.isWakeLockActive.value) {
          this.requestWakeLock();
        }
      });
    }
  }

  public async requestWakeLock(): Promise<boolean> {
    if (!this.isSupported.value) {
      return false;
    }

    try {
      this.isUserOptedIn = true;
      if (this.wakeLockSentinel && !this.wakeLockSentinel.released) {
        this.isWakeLockActive.value = true;
        return true;
      }

      this.wakeLockSentinel = await (navigator as any).wakeLock.request("screen");
      this.isWakeLockActive.value = true;

      this.wakeLockSentinel.addEventListener("release", () => {
        this.isWakeLockActive.value = false;
      });

      return true;
    } catch (err) {
      this.isWakeLockActive.value = false;
      return false;
    }
  }

  public async releaseWakeLock(): Promise<void> {
    this.isUserOptedIn = false;
    if (this.wakeLockSentinel) {
      try {
        await this.wakeLockSentinel.release();
      } catch {
        // Ignore release error
      }
      this.wakeLockSentinel = null;
      this.isWakeLockActive.value = false;
    }
  }

  public toggleWakeLock(enable: boolean): void {
    if (enable) {
      this.requestWakeLock();
    } else {
      this.releaseWakeLock();
    }
  }
}

export const wakeLockService = new ScreenWakeLockService();
