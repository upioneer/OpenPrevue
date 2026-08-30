<template>
  <div
    class="w-full h-full flex flex-col relative overflow-hidden"
    :class="{
      'scanlines-active': isScanlinesEnabled,
      'crt-screen-active': isCrtCurvatureEnabled
    }"
  >
    <HeaderBar />
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import HeaderBar from './components/HeaderBar.vue'
import { fetchSettings } from './api/client'

const isScanlinesEnabled = ref(true)
const isCrtCurvatureEnabled = ref(false)

onMounted(async () => {
  try {
    const s = await fetchSettings()
    if (s.scanline_intensity === '0') {
      isScanlinesEnabled.value = false
    }
    if (s.crt_curvature === '1') {
      isCrtCurvatureEnabled.value = true
    }
  } catch {
    // Default fallback
  }
})
</script>
