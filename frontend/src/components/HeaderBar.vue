<template>
  <header class="h-9 sm:h-10 bg-[#000044] border-b-2 border-[#333366] flex items-center justify-between px-3 sm:px-4 text-xs sm:text-sm font-mono select-none shrink-0 z-20">
    <div class="flex items-center space-x-2 sm:space-x-3">
      <router-link to="/" class="font-black tracking-wider text-[#FFFF00] hover:underline text-xs sm:text-sm md:text-base">
        OPENPREVUE // CHANNEL GUIDE
      </router-link>
      <span class="text-[#8888AA] font-bold">|</span>
      <span class="text-[#00FFFF] font-bold text-xs sm:text-sm hidden sm:inline">LIVE BROADCAST</span>
    </div>

    <div class="flex items-center space-x-2 sm:space-x-3">
      <!-- Spotify Quick Audio Launcher -->
      <button
        type="button"
        class="bg-[#1DB954] text-[#000033] hover:bg-[#FFFFFF] px-2 sm:px-2.5 py-0.5 sm:py-1 font-black text-xs tracking-wider border border-[#1DB954] cursor-pointer shadow-[0_0_8px_rgba(29,185,84,0.6)] transition-all shrink-0"
        @click="openSpotifyModal"
        title="Open Spotify Headend Player"
      >
        [ SPOTIFY ]
      </button>

      <!-- Master Audio Volume Slider & Mute Combo -->
      <div class="flex items-center space-x-1 sm:space-x-1.5 bg-[#000022] px-1.5 sm:px-2 py-0.5 border border-[#333366] shrink-0">
        <button
          type="button"
          class="px-1.5 py-0.2 text-[10px] sm:text-xs font-black uppercase transition cursor-pointer border"
          :class="audioSynth.isMuted.value ? 'bg-[#333366] text-[#FF6666] border-[#FF4444]' : 'bg-[#003300] text-[#00FF00] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.6)]'"
          :title="audioSynth.isMuted.value ? 'Click to unmute background audio' : 'Click to mute background audio'"
          @click="toggleMute"
        >
          {{ audioSynth.isMuted.value ? '[ MUTE ]' : '[ VOL ]' }}
        </button>

        <input
          type="range"
          min="0"
          max="100"
          step="1"
          :value="audioSynth.isMuted.value ? 0 : audioSynth.masterVolume.value"
          @input="onVolumeChange"
          class="w-12 sm:w-16 accent-[#00FF00] bg-[#000033] h-1.5 cursor-pointer"
          title="Master Volume Slider"
        />

        <span class="text-[10px] sm:text-xs font-mono font-bold w-7 text-right" :class="audioSynth.isMuted.value ? 'text-[#FF6666]' : 'text-[#00FF00]'">
          {{ audioSynth.isMuted.value ? '0%' : audioSynth.masterVolume.value + '%' }}
        </span>

        <div v-if="!audioSynth.isMuted.value && audioSynth.isAudioActive.value" class="hidden md:flex items-end space-x-0.5 h-3 text-[#00FF00]">
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-1.5"></span>
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-3"></span>
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-2"></span>
        </div>
      </div>

      <!-- Update Alert Badge -->
      <router-link
        v-if="updateAvailable"
        to="/settings"
        class="bg-[#FFFF00] text-[#000033] px-2 py-0.5 font-black text-xs animate-pulse tracking-wider hover:bg-white shadow-[0_0_8px_rgba(255,255,0,0.8)] cursor-pointer shrink-0"
        title="New OpenPrevue Version Available"
      >
        [ UPDATE: v{{ latestVersion }} ]
      </router-link>

      <router-link
        to="/"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors font-bold text-xs sm:text-sm shrink-0"
        :class="{ 'text-[#FFFF00] font-black': $route.path === '/' }"
      >
        [ GUIDE ]
      </router-link>
      <router-link
        to="/settings"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors font-bold text-xs sm:text-sm shrink-0"
        :class="{ 'text-[#FFFF00] font-black': $route.path === '/settings' }"
      >
        [ SETTINGS ]
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { fetchUpdateStatus } from '../api/client'
import { wsService } from '../services/websocket'
import { audioSynth } from '../services/audioSynth'
import { openSpotifyModal } from '../services/spotifyModalState'

const updateAvailable = ref(false)
const latestVersion = ref('')
let unsubscribeWs: (() => void) | null = null

function toggleMute() {
  audioSynth.toggleMute()
}

function onVolumeChange(event: Event) {
  const target = event.target as HTMLInputElement
  const val = parseInt(target.value, 10)
  if (!isNaN(val)) {
    audioSynth.setMasterVolume(val)
  }
}

async function checkUpdates() {
  try {
    const status = await fetchUpdateStatus()
    updateAvailable.value = status.update_available
    latestVersion.value = status.latest_version
  } catch {
    // Non-blocking update check failure
  }
}

onMounted(() => {
  checkUpdates()
  unsubscribeWs = wsService.on('update_available', (data: { latest_version: string }) => {
    updateAvailable.value = true
    if (data?.latest_version) {
      latestVersion.value = data.latest_version
    }
  })
})

onUnmounted(() => {
  if (unsubscribeWs) unsubscribeWs()
})
</script>
