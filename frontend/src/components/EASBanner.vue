<template>
  <div
    v-if="currentAlert"
    class="fixed top-0 left-0 right-0 z-50 bg-[#AA0000] border-b-4 border-[#FFFF00] text-[#FFFFFF] font-mono p-3 shadow-2xl animate-pulse select-none"
  >
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
      <!-- Left: Hazard Badge and Headline -->
      <div class="space-y-1 flex-1">
        <div class="flex items-center space-x-2">
          <span class="bg-[#FFFF00] text-[#AA0000] font-black text-xs px-2 py-0.5 tracking-widest uppercase">
            [{{ currentAlert.event_type }}]
          </span>
          <span class="text-xs text-[#FFFF77] font-bold uppercase tracking-wider">
            ISSUED BY: {{ currentAlert.sender }}
          </span>
        </div>
        <p class="text-sm font-black text-[#FFFFFF] tracking-wide uppercase">
          {{ currentAlert.headline }}
        </p>
        <p v-if="currentAlert.instruction" class="text-xs text-[#E0E0E0] line-clamp-2">
          {{ currentAlert.instruction }}
        </p>
      </div>

      <!-- Right: Area & Dismiss -->
      <div class="flex items-center space-x-3 self-end md:self-center">
        <div class="text-right hidden lg:block">
          <p class="text-[10px] text-[#FFAAAA]">AFFECTED AREA:</p>
          <p class="text-xs text-[#FFFF00] font-bold">{{ currentAlert.area_description }}</p>
        </div>
        <button
          class="bg-[#000033] hover:bg-[#000055] border-2 border-[#FFFF00] text-[#FFFF00] px-3 py-1.5 text-xs font-black tracking-widest uppercase cursor-pointer transition-colors shadow"
          @click="dismissAlert"
        >
          [ DISMISS ]
        </button>
      </div>
    </div>

    <!-- Auto-Dismiss Progress Bar -->
    <div class="w-full bg-[#550000] h-1 mt-2 overflow-hidden">
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
}

const currentAlert = ref<EmergencyAlertData | null>(null)
const progressPercent = ref(100)
let timerInterval: ReturnType<typeof setInterval> | null = null
let unsubscribeWs: (() => void) | null = null

function playEASAttentionTone() {
  try {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext
    if (!AudioCtx) return

    const ctx = new AudioCtx()
    const now = ctx.currentTime

    // 853 Hz oscillator
    const osc1 = ctx.createOscillator()
    osc1.frequency.setValueAtTime(853, now)

    // 960 Hz oscillator
    const osc2 = ctx.createOscillator()
    osc2.frequency.setValueAtTime(960, now)

    // Gain node to control volume
    const gainNode = ctx.createGain()
    gainNode.gain.setValueAtTime(0.08, now)
    gainNode.gain.exponentialRampToValueAtTime(0.0001, now + 1.2)

    osc1.connect(gainNode)
    osc2.connect(gainNode)
    gainNode.connect(ctx.destination)

    osc1.start(now)
    osc2.start(now)
    osc1.stop(now + 1.2)
    osc2.stop(now + 1.2)
  } catch (err) {
    console.debug('EAS Audio tone error:', err)
  }
}

function showAlert(alert: EmergencyAlertData, durationSeconds: number = 30) {
  currentAlert.value = alert
  progressPercent.value = 100
  playEASAttentionTone()

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
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  currentAlert.value = null
}

onMounted(() => {
  unsubscribeWs = wsService.on('emergency_alert', (alert: EmergencyAlertData) => {
    if (alert) {
      showAlert(alert, 30)
    }
  })
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (unsubscribeWs) unsubscribeWs()
})
</script>
