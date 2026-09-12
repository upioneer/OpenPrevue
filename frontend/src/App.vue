<template>
  <div
    class="w-full h-full flex flex-col relative overflow-hidden"
    :class="{
      'scanlines-active': isScanlinesEnabled,
      'crt-screen-active': isCrtCurvatureEnabled
    }"
  >
    <EASBanner />
    <HeaderBar v-if="!isKioskMode" />
    <router-view />
    <UpdateToast />
    <SpotifyPlayerModal
      :is-open="isSpotifyModalOpen"
      :custom-playlist-url="customPlaylistUrl"
      @open="openSpotifyModal"
      @close="closeSpotifyModal"
    />
    <UpdateModal
      :is-open="isUpdateModalOpen"
      :initial-target-version="updateModalTargetVersion"
      :diagnostic-mode="updateModalDiagnosticMode"
      @close="closeUpdateModal"
    />
    <OnboardingModal
      :is-open="isOnboardingModalOpen"
      @close="closeOnboardingModal"
    />
    <ChangelogModal
      :is-open="isChangelogModalOpen"
      :version="activeChangelogVersion"
      @close="closeChangelogModal"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import HeaderBar from './components/HeaderBar.vue'
import EASBanner from './components/EASBanner.vue'
import UpdateToast from './components/UpdateToast.vue'
import UpdateModal from './components/UpdateModal.vue'
import SpotifyPlayerModal from './components/SpotifyPlayerModal.vue'
import OnboardingModal from './components/OnboardingModal.vue'
import ChangelogModal from './components/ChangelogModal.vue'
import { fetchHealth, fetchSettings } from './api/client'
import { wsService } from './services/websocket'
import { audioSynth } from './services/audioSynth'
import { isSpotifyModalOpen, openSpotifyModal, closeSpotifyModal } from './services/spotifyModalState'
import { isUpdateModalOpen, updateModalTargetVersion, updateModalDiagnosticMode, closeUpdateModal } from './services/updateModalState'
import { isOnboardingModalOpen, isDismissedOnStartup, openOnboardingModal, closeOnboardingModal } from './services/onboardingModalState'
import { isChangelogModalOpen, activeChangelogVersion, checkShouldShowChangelog, closeChangelogModal, openChangelogModal } from './services/changelogModalState'

const route = useRoute()
const isKioskMode = computed(() => {
  return route.query.kiosk === '1' || route.query.kiosk === 'true' || route.query.header === '0'
})

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

onMounted(async () => {
  wsService.connect()
  loadDisplaySettings()
  audioSynth.initAutoPlayTrigger()

  unsubscribeSettings = wsService.on('settings_updated', () => {
    loadDisplaySettings()
  })

  const localOnboarded = localStorage.getItem('openprevue_onboarded')
  if (!isDismissedOnStartup() && !isKioskMode.value && localOnboarded === '1' && route.path === '/') {
    openOnboardingModal()
  } else if (!isKioskMode.value && route.path === '/') {
    try {
      const health = await fetchHealth()
      if (health.version && checkShouldShowChangelog(health.version)) {
        openChangelogModal(health.version)
      }
    } catch {
      // Ignore network errors on boot
    }
  }
})

onUnmounted(() => {
  if (unsubscribeSettings) unsubscribeSettings()
  wsService.disconnect()
})
</script>
