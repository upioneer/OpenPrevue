<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-3 select-none"
    @click.self="handleBackdropClick"
  >
    <div
      class="w-full max-w-2xl bg-[#000033] border-4 border-[#FFFF00] shadow-[0_0_35px_rgba(255,255,0,0.6)] font-mono text-xs text-[#E0E0E0] flex flex-col max-h-[90vh] overflow-hidden"
    >
      <!-- Title Bar -->
      <div class="bg-[#000066] border-b-2 border-[#FFFF00] px-3 py-2 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 bg-[#FFFF00] inline-block" :class="{ 'animate-pulse': isProcessing || isPolling }"></span>
          <span class="text-[#FFFF00] font-black tracking-wider text-xs sm:text-sm uppercase">
            [ OPENPREVUE HEADEND FIRMWARE UPGRADE ENGINE ]
          </span>
        </div>
        <button
          type="button"
          :disabled="isProcessing || isPolling"
          @click="closeModal"
          class="text-[#AAAAFF] hover:text-[#FFFF00] font-bold text-xs cursor-pointer px-2 py-0.5 border border-transparent hover:border-[#FFFF00] disabled:opacity-30 disabled:cursor-not-allowed"
          title="Close Dialog"
        >
          [ ESC / CLOSE ]
        </button>
      </div>

      <!-- Telemetry Ribbon -->
      <div class="bg-[#000022] border-b border-[#333366] px-4 py-2 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] shrink-0">
        <div>
          <span class="text-[#8888AA] block text-[10px]">CURRENT FIRMWARE:</span>
          <span class="text-[#FFFF00] font-bold">v{{ currentVersion }}</span>
        </div>
        <div>
          <span class="text-[#8888AA] block text-[10px]">TARGET RELEASE:</span>
          <span class="text-[#00FFFF] font-bold">v{{ resolvedTargetVersion }}</span>
        </div>
        <div>
          <span class="text-[#8888AA] block text-[10px]">ACTIVE STRATEGY:</span>
          <span class="font-bold text-[#00FF00] uppercase">{{ selectedMethod || capability?.detected_method || 'DETECTING...' }}</span>
        </div>
        <div>
          <span class="text-[#8888AA] block text-[10px]">STATUS:</span>
          <span
            class="font-bold"
            :class="{
              'text-[#00FF00]': statusState === 'ready' || statusState === 'success',
              'text-[#FFFF00] animate-pulse': statusState === 'working' || statusState === 'polling',
              'text-[#FF4444]': statusState === 'error',
            }"
          >
            {{ statusLabel }}
          </span>
        </div>
      </div>

      <!-- Content Area -->
      <div class="p-4 overflow-y-auto space-y-4 grow">
        <!-- Capability Description Banner -->
        <div class="bg-[#000044] border border-[#333366] p-3 text-[11px] leading-relaxed space-y-2">
          <div class="flex items-center justify-between border-b border-[#222255] pb-1">
            <span class="text-[#00FFFF] font-bold uppercase tracking-wider">
              [ RUNTIME CAPABILITY DISCOVERY ]
            </span>
            <span class="text-[#8888AA] text-[10px]">
              ENGINE: INDEPENDENT (NO WATCHTOWER REQUIRED)
            </span>
          </div>
          <p class="text-[#C0C0E0]">
            {{ capability?.description || 'Probing host environment for supported in-place update vectors...' }}
          </p>
          <div class="flex flex-wrap gap-2 pt-1 text-[10px]">
            <span
              class="px-2 py-0.5 border font-bold"
              :class="capability?.docker_socket_available ? 'bg-[#003300] border-[#00FF00] text-[#00FF00]' : 'bg-[#220000] border-[#662222] text-[#888888]'"
            >
              DOCKER_SOCKET: {{ capability?.docker_socket_available ? 'AVAILABLE' : 'OFFLINE' }}
            </span>
            <span
              class="px-2 py-0.5 border font-bold"
              :class="capability?.trigger_file_available ? 'bg-[#003300] border-[#00FF00] text-[#00FF00]' : 'bg-[#220000] border-[#662222] text-[#888888]'"
            >
              TRIGGER_FILE: {{ capability?.trigger_file_available ? 'ACTIVE' : 'OFFLINE' }}
            </span>
            <span
              class="px-2 py-0.5 border font-bold"
              :class="capability?.git_available ? 'bg-[#003300] border-[#00FF00] text-[#00FF00]' : 'bg-[#220000] border-[#662222] text-[#888888]'"
            >
              GIT_SOURCE: {{ capability?.git_available ? 'AVAILABLE' : 'OFFLINE' }}
            </span>
          </div>
        </div>

        <!-- Multi-Step Progress Matrix -->
        <div class="bg-[#000022] border border-[#333366] p-3 space-y-2">
          <div class="flex items-center justify-between text-[11px] mb-1">
            <span class="text-[#FFFF00] font-bold uppercase tracking-wider">UPGRADE PIPELINE STAGES</span>
            <span class="text-[#00FFFF] font-mono font-bold">{{ progressPercent }}%</span>
          </div>

          <!-- Retro ASCII Progress Bar -->
          <div class="bg-[#000011] border border-[#333366] p-1.5 font-mono text-[11px] text-[#00FF00] tracking-widest text-center">
            [{{ progressBarString }}]
          </div>

          <!-- Step Indicators -->
          <div class="grid grid-cols-1 sm:grid-cols-4 gap-1 text-[10px] pt-1">
            <div
              class="p-1.5 border text-center font-bold"
              :class="getStepClass(1)"
            >
              1. PRE-FLIGHT
            </div>
            <div
              class="p-1.5 border text-center font-bold"
              :class="getStepClass(2)"
            >
              2. PULL IMAGE
            </div>
            <div
              class="p-1.5 border text-center font-bold"
              :class="getStepClass(3)"
            >
              3. SWAP CONTAINER
            </div>
            <div
              class="p-1.5 border text-center font-bold"
              :class="getStepClass(4)"
            >
              4. HEALTH & RELOAD
            </div>
          </div>
        </div>

        <!-- Retro Terminal Log Console -->
        <div class="space-y-1">
          <div class="flex items-center justify-between text-[10px] text-[#8888AA]">
            <span>TELEMETRY CONSOLE STREAM:</span>
            <span>LINES: {{ logLines.length }}</span>
          </div>
          <div
            ref="terminalRef"
            class="bg-[#000011] border-2 border-[#333366] p-3 text-[11px] font-mono text-[#00FF00] h-44 overflow-y-auto whitespace-pre-wrap select-text leading-tight"
          >
            <div v-for="(line, idx) in logLines" :key="idx" class="leading-relaxed">
              <span class="text-[#888888]">{{ line.timestamp }}</span>
              <span :class="line.colorClass"> {{ line.text }}</span>
            </div>
            <div v-if="isProcessing || isPolling" class="text-[#FFFF00] animate-pulse">
              _
            </div>
          </div>
        </div>

        <!-- Strategy Override Selection -->
        <div v-if="!isProcessing && !isPolling" class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pt-1">
          <label class="text-[11px] text-[#A0A0C0]">Execution Strategy Override:</label>
          <select
            v-model="selectedMethod"
            class="bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none cursor-pointer"
          >
            <option
              v-for="m in capability?.available_methods || ['trigger_file']"
              :key="m"
              :value="m"
            >
              {{ formatMethodOption(m) }}
            </option>
          </select>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="bg-[#000022] border-t-2 border-[#FFFF00] p-3 flex flex-wrap items-center justify-between gap-2 shrink-0">
        <div class="text-[11px] text-[#A0A0C0]">
          <span v-if="reloadCountdown !== null" class="text-[#00FFFF] font-bold animate-pulse">
            HEADEND DETECTED ONLINE. RELOADING APPLICATION IN {{ reloadCountdown }}S...
          </span>
          <span v-else-if="isPolling" class="text-[#FFFF00] font-bold">
            POLLING HEADEND RECOVERY ON /api/v1/health...
          </span>
          <span v-else>
            READY TO UPGRADE TO v{{ resolvedTargetVersion }}
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <!-- Dry Run Button -->
          <button
            type="button"
            :disabled="isProcessing || isPolling"
            @click="runDryRun"
            class="bg-[#000066] hover:bg-[#000099] border border-[#00FFFF] text-[#00FFFF] px-3 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            [ TEST DRY-RUN ]
          </button>

          <!-- Live Apply Button -->
          <button
            type="button"
            :disabled="isProcessing || isPolling || reloadCountdown !== null"
            @click="runApplyUpdate"
            class="bg-[#FFFF00] hover:bg-[#FFFFFF] text-[#000033] px-4 py-1.5 text-xs font-black tracking-wider cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_12px_rgba(255,255,0,0.8)] transition-all"
          >
            {{ isProcessing ? '[ EXECUTING... ]' : (isPolling ? '[ AWAITING REBOOT... ]' : '[ APPLY LIVE UPGRADE ]') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { fetchHealth, fetchUpdateCapability, triggerApplyUpdate } from '../api/client'
import type { UpdateCapabilityResponse } from '../types'

interface LogEntry {
  timestamp: string
  text: string
  colorClass: string
}

const props = defineProps<{
  isOpen: boolean
  initialTargetVersion?: string | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const capability = ref<UpdateCapabilityResponse | null>(null)
const selectedMethod = ref<string>('')
const isProcessing = ref(false)
const isPolling = ref(false)
const hasError = ref(false)
const currentStep = ref(1)
const reloadCountdown = ref<number | null>(null)
const logLines = ref<LogEntry[]>([])
const terminalRef = ref<HTMLDivElement | null>(null)

const currentVersion = computed(() => capability.value?.current_version || '0.21.0')
const resolvedTargetVersion = computed(() => props.initialTargetVersion || capability.value?.latest_version || '0.22.0')

const statusState = computed<'ready' | 'working' | 'polling' | 'success' | 'error'>(() => {
  if (hasError.value) return 'error'
  if (reloadCountdown.value !== null || (currentStep.value === 4 && !isPolling.value)) return 'success'
  if (isPolling.value) return 'polling'
  if (isProcessing.value) return 'working'
  return 'ready'
})

const statusLabel = computed(() => {
  if (hasError.value) return 'ERROR'
  if (reloadCountdown.value !== null) return 'REBOOT DETECTED'
  if (isPolling.value) return 'AWAITING REBOOT'
  if (isProcessing.value) return 'UPDATING...'
  return 'READY'
})

const progressPercent = computed(() => {
  if (reloadCountdown.value !== null) return 100
  if (currentStep.value === 1) return 10
  if (currentStep.value === 2) return 45
  if (currentStep.value === 3) return 80
  if (currentStep.value === 4) return 95
  return 0
})

const progressBarString = computed(() => {
  const totalBlocks = 24
  const filledCount = Math.round((progressPercent.value / 100) * totalBlocks)
  const emptyCount = totalBlocks - filledCount
  return '█'.repeat(filledCount) + '░'.repeat(emptyCount)
})

function addLog(text: string, type: 'info' | 'warn' | 'success' | 'error' = 'info') {
  const now = new Date()
  const timestamp = `[${now.toTimeString().split(' ')[0]}]`
  let colorClass = 'text-[#00FF00]'
  if (type === 'warn') colorClass = 'text-[#FFFF00]'
  if (type === 'error') colorClass = 'text-[#FF4444]'
  if (type === 'success') colorClass = 'text-[#00FFFF]'

  logLines.value.push({ timestamp, text, colorClass })
  nextTick(() => {
    if (terminalRef.value) {
      terminalRef.value.scrollTop = terminalRef.value.scrollHeight
    }
  })
}

function getStepClass(stepNum: number) {
  if (stepNum < currentStep.value || (stepNum === 4 && reloadCountdown.value !== null)) {
    return 'bg-[#003300] border-[#00FF00] text-[#00FF00]'
  }
  if (stepNum === currentStep.value) {
    return 'bg-[#333300] border-[#FFFF00] text-[#FFFF00] animate-pulse'
  }
  return 'bg-[#000011] border-[#333366] text-[#666688]'
}

function formatMethodOption(method: string) {
  if (method === 'docker_socket') return 'DOCKER SOCKET (NATIVE CONTAINER SWAP)'
  if (method === 'trigger_file') return 'TRIGGER FILE (HOST WATCHER / CRON)'
  if (method === 'git') return 'GIT REPOSITORY (SOURCE CHECKOUT)'
  return method.toUpperCase()
}

async function loadCapability() {
  try {
    addLog('Querying host capabilities...', 'info')
    const cap = await fetchUpdateCapability()
    capability.value = cap
    selectedMethod.value = cap.detected_method
    addLog(`Host update capability resolved: ${cap.detected_method}`, 'success')
    addLog(`Target version: v${resolvedTargetVersion.value}`, 'info')
  } catch (err: any) {
    addLog(`Failed resolving capability: ${err.message}`, 'error')
  }
}

async function runDryRun() {
  isProcessing.value = true
  hasError.value = false
  currentStep.value = 1
  addLog('--- INITIATING UPGRADE DRY-RUN SIMULATION ---', 'warn')
  addLog(`Selected strategy: ${selectedMethod.value}`, 'info')

  try {
    const res = await triggerApplyUpdate({
      target_version: resolvedTargetVersion.value,
      dry_run: true,
      method: selectedMethod.value,
    })

    if (res.steps) {
      for (let i = 0; i < res.steps.length; i++) {
        addLog(`[STEP ${i + 1}/${res.steps.length}] ${res.steps[i]}`, 'info')
      }
    }
    addLog(res.message, 'success')
    addLog('Dry-run simulation completed successfully with zero modifications.', 'warn')
  } catch (err: any) {
    hasError.value = true
    addLog(`Dry-run simulation error: ${err.message}`, 'error')
  } finally {
    isProcessing.value = false
  }
}

async function runApplyUpdate() {
  isProcessing.value = true
  hasError.value = false
  currentStep.value = 2
  addLog('--- INITIATING LIVE IN-PLACE UPGRADE ---', 'warn')
  addLog(`Target image / version: v${resolvedTargetVersion.value}`, 'info')
  addLog(`Strategy: ${selectedMethod.value}`, 'info')

  try {
    currentStep.value = 3
    const res = await triggerApplyUpdate({
      target_version: resolvedTargetVersion.value,
      dry_run: false,
      method: selectedMethod.value,
    })

    addLog(res.message, 'success')
    if (res.trigger_file) {
      addLog(`Persistent trigger written to: ${res.trigger_file}`, 'info')
    }

    // Step 4: Health Polling Phase
    isProcessing.value = false
    isPolling.value = true
    currentStep.value = 4
    addLog('Entering health polling loop. Waiting for headend recovery...', 'warn')
    startHealthPolling()
  } catch (err: any) {
    hasError.value = true
    addLog(`Upgrade dispatch failed: ${err.message}`, 'error')
    isProcessing.value = false
  }
}

function startHealthPolling() {
  let attempts = 0
  const maxAttempts = 60
  const pollInterval = setInterval(async () => {
    attempts++
    try {
      addLog(`[PING ${attempts}] Probing /api/v1/health...`, 'info')
      const health = await fetchHealth()
      if (health && health.status === 'healthy') {
        clearInterval(pollInterval)
        addLog('HEADEND SERVICE DETECTED ONLINE AND HEALTHY!', 'success')
        isPolling.value = false
        triggerPageReload()
      }
    } catch {
      // Still restarting/offline
      if (attempts >= maxAttempts) {
        clearInterval(pollInterval)
        isPolling.value = false
        addLog('Health polling timed out. Please manually refresh your browser.', 'error')
      }
    }
  }, 2500)
}

function triggerPageReload() {
  reloadCountdown.value = 3
  const cdInterval = setInterval(() => {
    if (reloadCountdown.value !== null && reloadCountdown.value > 1) {
      reloadCountdown.value--
    } else {
      clearInterval(cdInterval)
      window.location.reload()
    }
  }, 1000)
}

function closeModal() {
  if (!isProcessing.value && !isPolling.value) {
    emit('close')
  }
}

function handleBackdropClick() {
  closeModal()
}

watch(
  () => props.isOpen,
  (newVal) => {
    if (newVal) {
      logLines.value = []
      currentStep.value = 1
      isProcessing.value = false
      isPolling.value = false
      reloadCountdown.value = null
      loadCapability()
    }
  },
  { immediate: true },
)

onMounted(() => {
  if (props.isOpen) {
    loadCapability()
  }
})
</script>
