<template>
  <div
    v-if="currentAlert"
    class="w-full bg-[#CC0000] text-white border-b-4 border-[#FFFF00] px-4 py-2 font-mono select-none z-50 animate-pulse shadow-2xl relative"
  >
    <div class="flex items-center justify-between">
      <!-- Left: High-Visibility Emergency Header & Pulsing Beacon -->
      <div class="flex items-center space-x-2 min-w-0">
        <span class="bg-[#FFFF00] text-[#000033] font-black px-2 py-0.5 text-xs tracking-wider uppercase whitespace-nowrap shrink-0">
          [ EMERGENCY ALERT SYSTEM ]
        </span>
        <span class="text-xs sm:text-sm font-black tracking-widest text-[#FFFF00] uppercase truncate">
          {{ currentAlert.event_type }}
        </span>
      </div>

      <!-- Right: Direct Dismiss Action Control & Countdown Telemetry -->
      <div class="flex items-center space-x-2 shrink-0">
        <span
          v-if="remainingSeconds > 0"
          class="text-[10px] font-mono font-bold text-[#FFFF00] hidden sm:inline-block opacity-90 whitespace-nowrap bg-[#000033]/60 px-2 py-0.5 border border-[#FFFF00]/40"
        >
          [ AUTO-CLOSES IN {{ formattedTimeRemaining }} ]
        </span>
        <button
          type="button"
          class="whitespace-nowrap shrink-0 bg-[#FFFF00] hover:bg-[#FFFFFF] text-[#000033] px-2.5 py-0.5 text-xs font-black uppercase cursor-pointer transition-all shadow-[0_0_8px_rgba(255,255,0,0.6)]"
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
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
const remainingSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null
let unsubscribeWs: (() => void) | null = null

const formattedTimeRemaining = computed(() => {
  const s = remainingSeconds.value
  if (s <= 0) return '00:00'
  const mins = Math.floor(s / 60)
  const secs = s % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

function showAlert(alert: EmergencyAlertData, durationSeconds: number = 300) {
  currentAlert.value = alert
  progressPercent.value = 100
  remainingSeconds.value = durationSeconds

  // Play one-shot sustained dual-tone attention signal (853 Hz + 960 Hz) capped between 6 and 10 seconds
  const toneDuration = Math.min(10, Math.max(6, Math.round(durationSeconds / 3)))
  audioSynth.playEASSiren(toneDuration)

  if (timerInterval) clearInterval(timerInterval)

  const startTime = Date.now()
  const durationMs = durationSeconds * 1000

  timerInterval = setInterval(() => {
    const elapsed = Date.now() - startTime
    const remainingFrac = Math.max(0, 1 - elapsed / durationMs)
    progressPercent.value = remainingFrac * 100
    remainingSeconds.value = Math.ceil(Math.max(0, (durationMs - elapsed) / 1000))

    if (remainingFrac <= 0) {
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
  remainingSeconds.value = 0
  progressPercent.value = 0
}

onMounted(() => {
  unsubscribeWs = wsService.on('emergency_alert', (alert: EmergencyAlertData) => {
    if (alert) {
      const displayDuration = alert.duration_seconds || 300
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
