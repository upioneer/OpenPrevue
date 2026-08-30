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
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import HeaderBar from './components/HeaderBar.vue'
import EASBanner from './components/EASBanner.vue'
import { fetchSettings } from './api/client'
import { wsService } from './services/websocket'

const isScanlinesEnabled = ref(true)
const isCrtCurvatureEnabled = ref(false)
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
  } catch {
    // Default fallback
  }
}

onMounted(() => {
  wsService.connect()
  loadDisplaySettings()

  unsubscribeSettings = wsService.on('settings_updated', () => {
    loadDisplaySettings()
  })
})

onUnmounted(() => {
  if (unsubscribeSettings) unsubscribeSettings()
  wsService.disconnect()
})
</script>
