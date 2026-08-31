<template>
  <div
    class="w-full h-full flex flex-col relative overflow-hidden"
    :class="{
      'scanlines-active': isScanlinesEnabled,
      'crt-screen-active': isCrtCurvatureEnabled
    }"
  >
    <EASBanner />
    <HeaderBar />
    <router-view />
    <UpdateToast />
    <SpotifyPlayerModal
      :is-open="isSpotifyModalOpen"
      :custom-playlist-url="customPlaylistUrl"
      @open="openSpotifyModal"
      @close="closeSpotifyModal"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import HeaderBar from './components/HeaderBar.vue'
import EASBanner from './components/EASBanner.vue'
import UpdateToast from './components/UpdateToast.vue'
import SpotifyPlayerModal from './components/SpotifyPlayerModal.vue'
import { fetchSettings } from './api/client'
import { wsService } from './services/websocket'
import { audioSynth } from './services/audioSynth'
import { isSpotifyModalOpen, openSpotifyModal, closeSpotifyModal } from './services/spotifyModalState'

const isScanlinesEnabled = ref(true)
const isCrtCurvatureEnabled = ref(false)
const customPlaylistUrl = ref('')
let unsubscribeSettings: (() => void) | null = null

async function loadDisplaySettings() {
  try {
    const s = await fetchSettings()
    if (s.scanline_intensity === '0') {
      isScanlinesEnabled.value = false
    } else {
      isScanlinesEnabled.value = true
    }
    if (s.crt_curvature === '1') {
      isCrtCurvatureEnabled.value = true
    } else {
      isCrtCurvatureEnabled.value = false
    }
    if (s.spotify_playlist_url) {
      customPlaylistUrl.value = s.spotify_playlist_url
    }
  } catch {
    // Default fallback
  }
}

onMounted(() => {
  wsService.connect()
  loadDisplaySettings()
  audioSynth.initAutoPlayTrigger()

  unsubscribeSettings = wsService.on('settings_updated', () => {
    loadDisplaySettings()
  })
})

onUnmounted(() => {
  if (unsubscribeSettings) unsubscribeSettings()
  wsService.disconnect()
})
</script>
