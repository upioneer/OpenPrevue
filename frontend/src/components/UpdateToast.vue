<template>
  <div
    v-if="isVisible"
    class="fixed bottom-6 right-6 z-50 max-w-sm sm:max-w-md bg-[#000044] border-2 border-[#FFFF00] shadow-[0_0_20px_rgba(255,255,0,0.7)] p-4 font-mono text-xs text-[#E0E0E0] select-none transition-all duration-300"
  >
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-[#333366] pb-1.5 mb-2">
      <div class="flex items-center space-x-2">
        <span class="w-2.5 h-2.5 bg-[#FFFF00] inline-block animate-pulse"></span>
        <span class="text-[#FFFF00] font-black tracking-wider text-xs">
          [ SYSTEM UPDATE AVAILABLE ]
        </span>
      </div>
      <button
        type="button"
        @click="dismiss"
        class="text-[#8888AA] hover:text-[#FFFF00] font-bold text-xs cursor-pointer px-1"
        title="Dismiss Notification"
      >
        [ X ]
      </button>
    </div>

    <!-- Body -->
    <p class="text-[11px] text-[#A0A0C0] mb-3 leading-relaxed">
      A new version of OpenPrevue (<strong class="text-[#00FFFF]">v{{ updateData?.latest_version }}</strong>) is available. Upgrading brings fresh retro features, headend DSP updates, and provider patches.
    </p>

    <!-- Actions -->
    <div class="flex items-center space-x-2">
      <router-link
        to="/settings"
        @click="dismiss"
        class="bg-[#FFFF00] text-[#000033] px-3 py-1 text-xs font-black hover:bg-[#FFFFFF] transition-all cursor-pointer shadow-[0_0_8px_rgba(255,255,0,0.8)]"
      >
        [ VIEW IN SETTINGS ]
      </router-link>
      <a
        v-if="updateData?.release_url"
        :href="updateData.release_url"
        target="_blank"
        rel="noopener noreferrer"
        class="bg-[#000080] border border-[#00FFFF] text-[#00FFFF] px-3 py-1 text-xs font-bold hover:bg-[#0000AA] cursor-pointer transition-colors"
      >
        [ GITHUB RELEASES ]
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { fetchUpdateStatus } from '../api/client'
import { wsService } from '../services/websocket'
import type { UpdateStatusResponse } from '../types'

const isVisible = ref(false)
const updateData = ref<UpdateStatusResponse | null>(null)
let unsubscribeWs: (() => void) | null = null

async function checkUpdates() {
  try {
    const status = await fetchUpdateStatus()
    if (status.update_available) {
      const dismissedVer = sessionStorage.getItem('openprevue_dismissed_update')
      if (dismissedVer !== status.latest_version) {
        updateData.value = status
        isVisible.value = true
      }
    }
  } catch {
    // Non-blocking update check failure
  }
}

function dismiss() {
  if (updateData.value?.latest_version) {
    sessionStorage.setItem('openprevue_dismissed_update', updateData.value.latest_version)
  }
  isVisible.value = false
}

onMounted(() => {
  checkUpdates()
  unsubscribeWs = wsService.on('update_available', (data: UpdateStatusResponse) => {
    if (data?.latest_version) {
      const dismissedVer = sessionStorage.getItem('openprevue_dismissed_update')
      if (dismissedVer !== data.latest_version) {
        updateData.value = data
        isVisible.value = true
      }
    }
  })
})

onUnmounted(() => {
  if (unsubscribeWs) unsubscribeWs()
})
</script>
