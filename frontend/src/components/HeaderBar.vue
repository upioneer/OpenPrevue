<template>
  <header class="h-8 bg-[#000044] border-b border-[#333366] flex items-center justify-between px-4 text-xs font-mono select-none">
    <div class="flex items-center space-x-3">
      <router-link to="/" class="font-bold tracking-wider text-[#FFFF00] hover:underline">
        OPENPREVUE // CHANNEL GUIDE
      </router-link>
      <span class="text-[#8888AA]">|</span>
      <span class="text-[#00FFFF]">LIVE BROADCAST</span>
    </div>

    <div class="flex items-center space-x-3">
      <!-- Update Alert Badge -->
      <router-link
        v-if="updateAvailable"
        to="/settings"
        class="bg-[#FFFF00] text-[#000033] px-2 py-0.5 font-black text-[10px] animate-pulse tracking-wider hover:bg-white shadow-[0_0_8px_rgba(255,255,0,0.8)] cursor-pointer"
        title="New OpenPrevue Version Available"
      >
        [ UPDATE: v{{ latestVersion }} ]
      </router-link>

      <router-link
        to="/"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors"
        :class="{ 'text-[#FFFF00] font-bold': $route.path === '/' }"
      >
        [ GUIDE ]
      </router-link>
      <router-link
        to="/settings"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors"
        :class="{ 'text-[#FFFF00] font-bold': $route.path === '/settings' }"
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
