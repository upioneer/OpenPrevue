<template>
  <header class="h-9 sm:h-10 bg-[#000044] border-b-2 border-[#333366] flex items-center justify-between px-3 sm:px-4 text-xs sm:text-sm font-mono select-none shrink-0 z-20">
    <div class="flex items-center space-x-3">
      <router-link to="/" class="font-black tracking-wider text-[#FFFF00] hover:underline text-xs sm:text-sm md:text-base">
        OPENPREVUE // CHANNEL GUIDE
      </router-link>
      <span class="text-[#8888AA] font-bold">|</span>
      <span class="text-[#00FFFF] font-bold text-xs sm:text-sm">LIVE BROADCAST</span>
    </div>

    <div class="flex items-center space-x-2 sm:space-x-3">
      <!-- Spotify Quick Audio Launcher -->
      <button
        type="button"
        class="bg-[#1DB954] text-[#000033] hover:bg-[#FFFFFF] px-2.5 py-0.5 sm:py-1 font-black text-xs sm:text-sm tracking-wider border border-[#1DB954] cursor-pointer shadow-[0_0_8px_rgba(29,185,84,0.6)] transition-all"
        @click="openSpotifyModal"
        title="Open Spotify Headend Player"
      >
        [ SPOTIFY ]
      </button>

      <!-- Master Audio Quick Toggle -->
      <button
        type="button"
        class="px-2.5 py-0.5 sm:py-1 font-black text-xs sm:text-sm tracking-wider border cursor-pointer transition-all"
        :class="audioSynth.isAudioActive.value
          ? 'bg-[#003300] text-[#00FF00] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.6)]'
          : 'bg-[#332200] text-[#FFAA00] border-[#FFAA00] hover:border-[#FFFF00] hover:text-[#FFFF00]'"
        @click="audioSynth.toggleMasterAudio"
        :title="audioSynth.isAudioActive.value ? 'Click to Mute Background Audio' : 'Click to Enable 1990s TV Background Audio'"
      >
        {{ audioSynth.isAudioActive.value ? '[ AUDIO: ON ]' : '[ AUDIO: MUTED ]' }}
      </button>

      <!-- Update Alert Badge -->
      <router-link
        v-if="updateAvailable"
        to="/settings"
        class="bg-[#FFFF00] text-[#000033] px-2 py-0.5 font-black text-xs animate-pulse tracking-wider hover:bg-white shadow-[0_0_8px_rgba(255,255,0,0.8)] cursor-pointer"
        title="New OpenPrevue Version Available"
      >
        [ UPDATE: v{{ latestVersion }} ]
      </router-link>

      <router-link
        to="/"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors font-bold text-xs sm:text-sm"
        :class="{ 'text-[#FFFF00] font-black': $route.path === '/' }"
      >
        [ GUIDE ]
      </router-link>
      <router-link
        to="/settings"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors font-bold text-xs sm:text-sm"
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
