<template>
  <div
    v-if="isVisible"
    class="fixed bottom-6 right-6 z-50 w-auto max-w-[calc(100vw-3rem)] sm:max-w-lg bg-[#000044] border-2 border-[#FFFF00] shadow-[0_0_20px_rgba(255,255,0,0.7)] p-4 font-mono text-xs text-[#E0E0E0] select-none transition-all duration-300"
  >
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-[#333366] pb-1.5 mb-2">
      <div class="flex items-center space-x-2 min-w-0">
        <span class="w-2.5 h-2.5 bg-[#FFFF00] inline-block animate-pulse shrink-0"></span>
        <span class="text-[#FFFF00] font-black tracking-wider text-xs whitespace-nowrap">
          [ SYSTEM UPDATE AVAILABLE ]
        </span>
      </div>
      <div class="flex items-center space-x-2 shrink-0">
        <button
          type="button"
          @click="snooze(24)"
          class="text-[#8888AA] hover:text-[#00FFFF] font-bold text-[10px] cursor-pointer px-1 whitespace-nowrap"
          title="Snooze update notification for 24 hours"
        >
          [ SNOOZE 24H ]
        </button>
        <button
          type="button"
          @click="dismiss"
          class="text-[#8888AA] hover:text-[#FFFF00] font-bold text-xs cursor-pointer px-1 whitespace-nowrap"
          title="Dismiss notification for this version"
        >
          [ X ]
        </button>
      </div>
    </div>

    <!-- Body -->
    <p class="text-[11px] text-[#A0A0C0] mb-2 leading-relaxed">
      A new version of OpenPrevue (<strong class="text-[#00FFFF]">v{{ updateData?.latest_version }}</strong>) is available (running <span class="text-[#FFFF00]">v{{ updateData?.current_version }}</span>). Upgrading brings new retro broadcast features, scheduler enhancements, and provider patches.
    </p>

    <!-- CLI Guidance Card (Recommended) -->
    <div class="bg-[#000022] border border-[#333366] p-2.5 mb-3 space-y-1.5">
      <div class="flex items-center justify-between text-[10px]">
        <span class="text-[#00FFFF] font-bold tracking-wider uppercase">
          RECOMMENDED UPGRADE (HOST TERMINAL):
        </span>
        <div class="flex items-center space-x-1.5">
          <button
            type="button"
            @click="activeCliTab = 'docker'"
            :class="activeCliTab === 'docker' ? 'text-[#FFFF00] font-black underline' : 'text-[#8888AA] hover:text-[#E0E0E0]'"
            class="cursor-pointer text-[10px]"
          >
            DOCKER
          </button>
          <span class="text-[#444466]">|</span>
          <button
            type="button"
            @click="activeCliTab = 'git'"
            :class="activeCliTab === 'git' ? 'text-[#FFFF00] font-black underline' : 'text-[#8888AA] hover:text-[#E0E0E0]'"
            class="cursor-pointer text-[10px]"
          >
            GIT
          </button>
        </div>
      </div>

      <div class="flex items-center justify-between gap-2 bg-[#000011] p-1.5 border border-[#222255]">
        <code class="text-[10px] sm:text-[11px] text-[#00FF00] font-mono truncate select-all">
          {{ activeCliTab === 'docker' ? 'docker compose pull && docker compose up -d' : 'git pull origin main && npm --prefix frontend run build' }}
        </code>
        <button
          type="button"
          @click="copyCliCommand"
          class="whitespace-nowrap shrink-0 bg-[#000066] hover:bg-[#000088] text-[#FFFF00] px-2 py-0.5 text-[10px] font-bold border border-[#FFFF00] cursor-pointer transition-colors"
          title="Copy command to clipboard"
        >
          [ {{ isCopied ? 'COPIED!' : 'COPY' }} ]
        </button>
      </div>
      <p class="text-[9px] text-[#8888AA] leading-tight">
        CLI upgrade is recommended for container stability, rollback capability, and security.
      </p>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap items-center gap-2 pt-0.5">
      <button
        type="button"
        @click="handleUpgradeNow"
        class="whitespace-nowrap shrink-0 bg-[#FFFF00] text-[#000033] px-3 py-1 text-xs font-black hover:bg-[#FFFFFF] transition-all cursor-pointer shadow-[0_0_8px_rgba(255,255,0,0.8)]"
      >
        [ UPGRADE IN-PLACE ]
      </button>
      <router-link
        to="/settings?tab=updates"
        @click="dismiss"
        class="whitespace-nowrap shrink-0 bg-[#000080] border border-[#FFFF00] text-[#FFFF00] px-3 py-1 text-xs font-bold hover:bg-[#0000AA] cursor-pointer transition-colors"
      >
        [ SETTINGS ]
      </router-link>
      <a
        v-if="updateData?.release_url"
        :href="updateData.release_url"
        target="_blank"
        rel="noopener noreferrer"
        class="whitespace-nowrap shrink-0 bg-[#000080] border border-[#00FFFF] text-[#00FFFF] px-3 py-1 text-xs font-bold hover:bg-[#0000AA] cursor-pointer transition-colors"
      >
        [ GITHUB ]
      </a>
      <button
        type="button"
        @click="dismiss"
        class="whitespace-nowrap shrink-0 bg-[#000044] border border-[#8888AA] text-[#A0A0C0] hover:text-[#FFFF00] hover:border-[#FFFF00] px-2.5 py-1 text-xs font-bold cursor-pointer transition-colors ml-auto"
        title="Don't show again for this version"
      >
        [ DISMISS ]
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchUpdateStatus } from '../api/client'
import { wsService } from '../services/websocket'
import { openUpdateModal } from '../services/updateModalState'
import type { UpdateStatusResponse } from '../types'

const route = useRoute()
const isVisible = ref(false)
const updateData = ref<UpdateStatusResponse | null>(null)
const activeCliTab = ref<'docker' | 'git'>('docker')
const isCopied = ref(false)
let copyTimeout: ReturnType<typeof setTimeout> | null = null
let unsubscribeWs: (() => void) | null = null

const isKioskMode = computed(() => {
  return route.query.kiosk === 'true' || route.query.kiosk === '1' || window.location.search.includes('kiosk=')
})

function isDismissedOrSnoozed(ver: string): boolean {
  try {
    const snoozedUntil = Number(localStorage.getItem('openprevue_snoozed_update_until') || '0')
    if (Date.now() < snoozedUntil) {
      return true
    }
    const dismissedLocal = localStorage.getItem('openprevue_dismissed_update')
    const dismissedSession = sessionStorage.getItem('openprevue_dismissed_update')
    return dismissedLocal === ver || dismissedSession === ver
  } catch {
    return false
  }
}

async function checkUpdates() {
  if (isKioskMode.value) return
  try {
    const status = await fetchUpdateStatus()
    if (status.update_available && status.latest_version) {
      if (!isDismissedOrSnoozed(status.latest_version)) {
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
    try {
      localStorage.setItem('openprevue_dismissed_update', updateData.value.latest_version)
      sessionStorage.setItem('openprevue_dismissed_update', updateData.value.latest_version)
    } catch {
      // Ignore storage write error
    }
  }
  isVisible.value = false
}

function snooze(hours = 24) {
  try {
    const until = Date.now() + (hours * 3600 * 1000)
    localStorage.setItem('openprevue_snoozed_update_until', String(until))
  } catch {
    // Ignore storage write error
  }
  isVisible.value = false
}

async function copyCliCommand() {
  const cmd = activeCliTab.value === 'docker'
    ? 'docker compose pull && docker compose up -d'
    : 'git pull origin main && npm --prefix frontend run build'
  try {
    await navigator.clipboard.writeText(cmd)
    isCopied.value = true
    if (copyTimeout) clearTimeout(copyTimeout)
    copyTimeout = setTimeout(() => {
      isCopied.value = false
    }, 2500)
  } catch {
    // Fallback if clipboard API restricted
  }
}

function handleUpgradeNow() {
  const targetVer = updateData.value?.latest_version
  dismiss()
  openUpdateModal(targetVer)
}

onMounted(() => {
  checkUpdates()
  unsubscribeWs = wsService.on('update_available', (data: UpdateStatusResponse) => {
    if (isKioskMode.value) return
    if (data?.latest_version && !isDismissedOrSnoozed(data.latest_version)) {
      updateData.value = data
      isVisible.value = true
    }
  })
})

onUnmounted(() => {
  if (unsubscribeWs) unsubscribeWs()
  if (copyTimeout) clearTimeout(copyTimeout)
})
</script>
