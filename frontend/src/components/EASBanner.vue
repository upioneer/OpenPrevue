<template>
  <div
    v-if="currentAlert"
    class="w-full bg-[#CC0000] text-white border-b-4 border-[#FFFF00] px-4 py-2 font-mono select-none z-50 animate-pulse shadow-2xl relative"
  >
    <div class="flex items-center justify-between">
      <!-- Left: High-Visibility Emergency Header & Pulsing Beacon -->
      <div class="flex items-center space-x-2">
        <span class="bg-[#FFFF00] text-[#000033] font-black px-2 py-0.5 text-xs tracking-wider uppercase">
          [ EMERGENCY ALERT SYSTEM ]
        </span>
        <span class="text-xs sm:text-sm font-black tracking-widest text-[#FFFF00] uppercase">
          {{ currentAlert.event_type }}
        </span>
      </div>

      <!-- Right: Direct Dismiss Action Control -->
      <div class="flex items-center space-x-2">
        <button
          type="button"
          class="bg-[#FFFF00] hover:bg-[#FFFFFF] text-[#000033] px-2 py-0.5 text-xs font-black uppercase cursor-pointer transition-all"
          @click="dismissAlert"
        >
          [ DISMISS ]
        </button>
      </div>
    </div>

    <!-- Alert Headline & Scope -->
    <div class="mt-1">
      <div class="text-sm sm:text-base font-black text-[#FFFF00] uppercase leading-tight">
        {{ currentAlert.headline }}
      </div>
      <div class="text-xs text-[#E0E0E0] mt-0.5 font-bold">
        AFFECTED AREA: <span class="text-white">{{ currentAlert.area_description }}</span>
      </div>
      <div v-if="currentAlert.instruction" class="text-xs text-[#FFFFCC] mt-0.5 font-medium">
        {{ currentAlert.instruction }}
      </div>
    </div>

    <!-- Live Duration Depletion Progress Bar -->
    <div class="w-full bg-[#550000] h-1.5 mt-2 overflow-hidden">
      <div
        class="bg-[#FFFF00] h-full transition-all duration-100 ease-linear"
        :style="{ width: `${progressPercent}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { wsService } from '../services/websocket'
import { audioSynth } from '../services/audioSynth'

export interface EmergencyAlertData {
  id: string
  sender: string
  headline: string
  severity: string
  urgency: string
  event_type: string
  area_description: string
  instruction?: string
  effective_at: string
  expires_at: string
  is_active: boolean
  duration_seconds?: number
}

const currentAlert = ref<EmergencyAlertData | null>(null)
const progressPercent = ref(100)
let timerInterval: ReturnType<typeof setInterval> | null = null
let unsubscribeWs: (() => void) | null = null

function showAlert(alert: EmergencyAlertData, durationSeconds: number = 30) {
  currentAlert.value = alert
  progressPercent.value = 100

  // Play one-shot sustained 8-second dual-tone attention signal (853 Hz + 960 Hz) then auto-stop
  const toneDuration = Math.min(10, Math.max(6, Math.round(durationSeconds / 3)))
  audioSynth.playEASSiren(toneDuration)

  if (timerInterval) clearInterval(timerInterval)

  const startTime = Date.now()
  const durationMs = durationSeconds * 1000

  timerInterval = setInterval(() => {
    const elapsed = Date.now() - startTime
    const remaining = Math.max(0, 1 - elapsed / durationMs)
    progressPercent.value = remaining * 100

    if (remaining <= 0) {
      dismissAlert()
    }
  }, 100)
}

function dismissAlert() {
  audioSynth.stopEASSiren()
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  currentAlert.value = null
}

onMounted(() => {
  unsubscribeWs = wsService.on('emergency_alert', (alert: EmergencyAlertData) => {
    if (alert) {
      const displayDuration = alert.duration_seconds || 30
      showAlert(alert, displayDuration)
    }
  })
})

onUnmounted(() => {
  audioSynth.stopEASSiren()
  if (timerInterval) clearInterval(timerInterval)
  if (unsubscribeWs) unsubscribeWs()
})
</script>
