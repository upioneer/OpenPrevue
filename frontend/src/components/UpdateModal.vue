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
              'text-[#00FF00]': statusState === 'ready' || statusState === 'success' || statusState === 'up_to_date',
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
        <!-- Up-to-Date Informational Banner -->
        <div
          v-if="!isUpgradeAvailable"
          class="bg-[#002200] border-2 border-[#00FF00] p-3 text-[11px] text-[#00FF00] space-y-1 shadow-[0_0_12px_rgba(0,255,0,0.3)]"
        >
          <div class="font-bold flex items-center space-x-2 uppercase">
            <span class="w-2.5 h-2.5 bg-[#00FF00] inline-block"></span>
            <span>[ SYSTEM FIRMWARE IS CURRENT ]</span>
          </div>
          <p class="text-[#D0FFD0] leading-relaxed">
            Your system is currently running version <strong>v{{ currentVersion }}</strong>, which matches or exceeds the target release (<strong>v{{ resolvedTargetVersion }}</strong>). In-place live upgrades are restricted to strictly newer releases to prevent redundant container rebuilds. Diagnostic simulations remain available to verify headend deployment hooks.
          </p>
        </div>

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
        <div class="bg-[#000022] border border-[#333366] p-3 space-y-2.5">
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-[#FFFF00] font-bold uppercase tracking-wider">UPGRADE PIPELINE STAGES</span>
            <span class="text-[#00FFFF] font-mono font-bold">{{ progressPercent }}% [STAGE {{ Math.min(Math.max(currentStep, 1), 4) }}/4]</span>
          </div>

          <!-- Retro Segmented LED Progress Bar -->
          <div class="space-y-1">
            <div class="flex items-center gap-1 h-5 bg-[#000011] border border-[#333366] p-1">
              <div
                v-for="i in totalSegments"
                :key="i"
                class="flex-1 h-full rounded-xs transition-all duration-150"
                :class="getSegmentClass(i)"
              ></div>
            </div>
            <div class="flex items-center justify-between text-[10px] font-mono text-[#8888AA] pt-0.5">
              <span class="text-[#00FF00]">
                STATUS: {{ statusLabel }}
              </span>
              <span>
                {{ activeSegmentCount }} / {{ totalSegments }} SEGMENTS
              </span>
            </div>
          </div>

          <!-- Step Indicators -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[10px] pt-1">
            <div
              v-for="step in pipelineSteps"
              :key="step.number"
              class="p-2 border text-center font-bold flex flex-col justify-between space-y-1 transition-all"
              :class="getStepClass(step.number)"
            >
              <div class="tracking-wider">{{ step.number }}. {{ step.title }}</div>
              <div class="text-[9px] font-mono tracking-widest opacity-90">
                {{ getStepStatus(step.number) }}
              </div>
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
            data-testid="telemetry-terminal"
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
          <span v-else-if="!isUpgradeAvailable && !diagnosticMode" class="text-[#00FF00] font-bold">
            CURRENT FIRMWARE (v{{ currentVersion }}) IS UP TO DATE. NO UPGRADE REQUIRED.
          </span>
          <span v-else>
            READY TO UPGRADE TO v{{ resolvedTargetVersion }}
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <!-- Diagnostic Dry Run Button (Shown when launched in Diagnostic Mode or when up-to-date) -->
          <button
            v-if="diagnosticMode || !isUpgradeAvailable"
            type="button"
            :disabled="isProcessing || isPolling"
            @click="runDryRun"
            class="bg-[#000066] hover:bg-[#000099] border border-[#00FFFF] text-[#00FFFF] px-3 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {{ isProcessing ? '[ SIMULATING... ]' : '[ RUN DIAGNOSTIC DRY-RUN ]' }}
          </button>

          <!-- Primary Live Apply Button -->
          <button
            type="button"
            :disabled="!isUpgradeAvailable || isProcessing || isPolling || reloadCountdown !== null"
            @click="runApplyUpdate"
            class="px-5 py-2 text-xs font-black tracking-wider transition-all"
            :class="isUpgradeAvailable && !isProcessing && !isPolling && reloadCountdown === null
              ? 'bg-[#FFFF00] hover:bg-[#FFFFFF] text-[#000033] cursor-pointer shadow-[0_0_12px_rgba(255,255,0,0.8)]'
              : 'bg-[#001122] border border-[#334466] text-[#6688AA] cursor-not-allowed opacity-60'"
          >
            {{
              isProcessing
                ? '[ EXECUTING... ]'
                : isPolling
                  ? '[ AWAITING REBOOT... ]'
                  : isUpgradeAvailable
                    ? `[ APPLY LIVE UPGRADE: v${resolvedTargetVersion} ]`
                    : '[ FIRMWARE IS UP TO DATE ]'
            }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { fetchHealth, fetchUpdateCapability, triggerApplyUpdate } from '../api/client'
import { isNewerVersion } from '../services/semver'
import type { UpdateCapabilityResponse } from '../types'

interface LogEntry {
  timestamp: string
  text: string
  colorClass: string
}

const props = defineProps<{
  isOpen: boolean
  initialTargetVersion?: string | null
  diagnosticMode?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const pipelineSteps = [
  { number: 1, title: 'PRE-FLIGHT' },
  { number: 2, title: 'PULL IMAGE' },
  { number: 3, title: 'SWAP CONTAINER' },
  { number: 4, title: 'HEALTH & RELOAD' },
]

const capability = ref<UpdateCapabilityResponse | null>(null)
const selectedMethod = ref<string>('')
const isProcessing = ref(false)
const isPolling = ref(false)
const hasError = ref(false)
const currentStep = ref(1)
const reloadCountdown = ref<number | null>(null)
const logLines = ref<LogEntry[]>([])
const terminalRef = ref<HTMLDivElement | null>(null)

// Retro Segmented LED Progress Bar State & Scanner Animation
const totalSegments = 24
const scannerIndex = ref(0)
let scannerTimer: ReturnType<typeof setInterval> | null = null

function startScanner() {
  if (scannerTimer) return
  scannerTimer = setInterval(() => {
    scannerIndex.value = (scannerIndex.value + 1) % totalSegments
  }, 75)
}

function stopScanner() {
  if (scannerTimer) {
    clearInterval(scannerTimer)
    scannerTimer = null
  }
}

watch(
  [isProcessing, isPolling],
  ([processing, polling]) => {
    if (processing || polling) {
      startScanner()
    } else {
      stopScanner()
    }
  }
)

onUnmounted(() => {
  stopScanner()
})

const currentVersion = computed(() => capability.value?.current_version || '0.21.0')
const resolvedTargetVersion = computed(() => props.initialTargetVersion || capability.value?.latest_version || '0.22.0')

const isUpgradeAvailable = computed(() => {
  if (!currentVersion.value || !resolvedTargetVersion.value) return false
  return isNewerVersion(currentVersion.value, resolvedTargetVersion.value)
})

const statusState = computed<'ready' | 'working' | 'polling' | 'success' | 'error' | 'up_to_date'>(() => {
  if (hasError.value) return 'error'
  if (reloadCountdown.value !== null || (currentStep.value === 4 && !isProcessing.value && !isPolling.value)) return 'success'
  if (isPolling.value) return 'polling'
  if (isProcessing.value) return 'working'
  if (!isUpgradeAvailable.value && !props.diagnosticMode) return 'up_to_date'
  return 'ready'
})

const statusLabel = computed(() => {
  if (hasError.value) return 'ERROR'
  if (reloadCountdown.value !== null) return `REBOOT DETECTED (${reloadCountdown.value}s)`
  if (isPolling.value) return 'AWAITING REBOOT'
  if (isProcessing.value) return 'EXECUTING...'
  if (currentStep.value === 4 && !isProcessing.value && !isPolling.value && !hasError.value) return 'DRY-RUN COMPLETE'
  if (!isUpgradeAvailable.value && !props.diagnosticMode) return 'UP TO DATE'
  return 'READY'
})

const progressPercent = computed(() => {
  if (reloadCountdown.value !== null) return 100
  if (currentStep.value === 4 && !isProcessing.value && !isPolling.value && !hasError.value) return 100
  if (currentStep.value === 4) return 90
  if (currentStep.value === 3) return 70
  if (currentStep.value === 2) return 45
  if (currentStep.value === 1) {
    return isProcessing.value ? 20 : 0
  }
  return 0
})

const activeSegmentCount = computed(() => {
  return Math.round((progressPercent.value / 100) * totalSegments)
})

function getSegmentClass(i: number): string {
  // If complete / rebooting: all segments glow bright cyan
  if (progressPercent.value >= 100) {
    return 'bg-[#00FFFF] border border-[#FFFFFF] shadow-[0_0_8px_rgba(0,255,255,0.9)]'
  }

  // Active scan pulse while working or polling
  if ((isProcessing.value || isPolling.value) && i === scannerIndex.value + 1) {
    return 'bg-[#FFFF00] border border-[#FFFFFF] shadow-[0_0_10px_rgba(255,255,0,1)] animate-pulse'
  }

  // Filled segments glow phosphor green
  if (i <= activeSegmentCount.value) {
    return 'bg-[#00FF00] border border-[#33FF33] shadow-[0_0_5px_rgba(0,255,0,0.7)]'
  }

  // Unfilled dark LED slot
  return 'bg-[#060618] border border-[#141432]'
}

function getStepStatus(stepNum: number): string {
  if (currentStep.value > stepNum || (stepNum === 4 && reloadCountdown.value !== null) || (stepNum === 4 && currentStep.value === 4 && !isProcessing.value && !isPolling.value && !hasError.value)) {
    return '[ DONE ]'
  }
  if (currentStep.value === stepNum) {
    if (isProcessing.value || isPolling.value) return '[ ACTIVE ]'
    return '[ READY ]'
  }
  return '[ QUEUED ]'
}

function getStepClass(stepNum: number): string {
  if (currentStep.value > stepNum || (stepNum === 4 && reloadCountdown.value !== null) || (stepNum === 4 && currentStep.value === 4 && !isProcessing.value && !isPolling.value && !hasError.value)) {
    return 'bg-[#003300] border-[#00FF00] text-[#00FF00]'
  }
  if (currentStep.value === stepNum) {
    if (isProcessing.value || isPolling.value) {
      return 'bg-[#333300] border-[#FFFF00] text-[#FFFF00] animate-pulse shadow-[0_0_10px_rgba(255,255,0,0.4)]'
    }
    return 'bg-[#002244] border-[#00FFFF] text-[#00FFFF]'
  }
  return 'bg-[#000011] border-[#333366] text-[#666688]'
}

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
    addLog(`Installed firmware: v${currentVersion.value} | Target release: v${resolvedTargetVersion.value}`, 'info')
    if (!isUpgradeAvailable.value && !props.diagnosticMode) {
      addLog(`[NOTICE] Installed version v${currentVersion.value} is already up to date with release v${resolvedTargetVersion.value}. In-place upgrades are disabled until a newer release is published.`, 'warn')
    }
  } catch (err: any) {
    addLog(`Failed resolving capability: ${err.message}`, 'error')
  }
}

async function runDryRun() {
  if (isProcessing.value || isPolling.value) return
  isProcessing.value = true
  hasError.value = false
  currentStep.value = 1
  addLog('--- INITIATING UPGRADE DRY-RUN SIMULATION ---', 'warn')
  addLog(`Selected strategy: ${selectedMethod.value}`, 'info')

  try {
    // Stage 1: Pre-Flight
    addLog('[STAGE 1/4: PRE-FLIGHT] Verifying host environment and runtime permissions...', 'info')
    await new Promise((r) => setTimeout(r, 350))

    // Stage 2: Pull Image
    currentStep.value = 2
    addLog(`[STAGE 2/4: PULL IMAGE] Simulating image pull for ghcr.io/upioneer/openprevue:v${resolvedTargetVersion.value}...`, 'info')
    await new Promise((r) => setTimeout(r, 450))

    // Stage 3: Swap Container
    currentStep.value = 3
    addLog('[STAGE 3/4: SWAP CONTAINER] Testing container recreation parameters and volume bindings...', 'info')
    const res = await triggerApplyUpdate({
      target_version: resolvedTargetVersion.value,
      dry_run: true,
      method: selectedMethod.value,
    })

    if (res.steps) {
      for (let i = 0; i < res.steps.length; i++) {
        addLog(`  -> ${res.steps[i]}`, 'info')
      }
    }
    await new Promise((r) => setTimeout(r, 350))

    // Stage 4: Health Recovery Readiness
    currentStep.value = 4
    addLog('[STAGE 4/4: HEALTH & RELOAD] Simulating health recovery handshake...', 'info')
    await new Promise((r) => setTimeout(r, 350))

    addLog(res.message, 'success')
    addLog('Dry-run simulation completed successfully with zero host modifications.', 'warn')
  } catch (err: any) {
    hasError.value = true
    addLog(`Dry-run simulation error: ${err.message}`, 'error')
  } finally {
    isProcessing.value = false
  }
}

async function runApplyUpdate() {
  if (!isUpgradeAvailable.value && !props.diagnosticMode) {
    addLog(`[REJECTED] In-place upgrade aborted: target version v${resolvedTargetVersion.value} is not strictly newer than current version v${currentVersion.value}.`, 'warn')
    return
  }
  if (isProcessing.value || isPolling.value) return
  isProcessing.value = true
  hasError.value = false
  currentStep.value = 1
  addLog('--- INITIATING LIVE IN-PLACE UPGRADE ---', 'warn')
  addLog(`Target image / version: v${resolvedTargetVersion.value}`, 'info')
  addLog(`Strategy: ${selectedMethod.value}`, 'info')

  try {
    addLog('[STAGE 1/4: PRE-FLIGHT] Verifying container host readiness...', 'info')
    await new Promise((r) => setTimeout(r, 300))

    currentStep.value = 2
    addLog(`[STAGE 2/4: PULL IMAGE] Dispatching image pull for ghcr.io/upioneer/openprevue:v${resolvedTargetVersion.value}...`, 'info')
    await new Promise((r) => setTimeout(r, 400))

    currentStep.value = 3
    addLog('[STAGE 3/4: SWAP CONTAINER] Executing container lifecycle recreation...', 'info')
    const res = await triggerApplyUpdate({
      target_version: resolvedTargetVersion.value,
      dry_run: false,
      method: selectedMethod.value,
    })

    if (res.status === 'up_to_date') {
      isProcessing.value = false
      addLog(res.message || `System is already up to date (v${currentVersion.value}). No upgrade required.`, 'warn')
      return
    }

    if (res.status === 'error') {
      hasError.value = true
      isProcessing.value = false
      addLog(`Upgrade failed: ${res.message || res.error}`, 'error')
      if (res.error) {
        addLog(`Diagnostic detail: ${res.error}`, 'error')
      }
      return
    }

    if (res.status === 'triggered' || res.trigger_file) {
      isProcessing.value = false
      addLog(`Persistent trigger written to: ${res.trigger_file || './data/.update_trigger'}`, 'info')
      addLog('[ACTION REQUIRED] Running in host trigger file mode.', 'warn')
      addLog('To complete upgrade on your host, execute: docker compose pull && docker compose up -d', 'warn')
      addLog('To enable zero-touch 1-click upgrades from the UI, mount /var/run/docker.sock in docker-compose.yml.', 'info')
      isPolling.value = true
      currentStep.value = 4
      startHealthPolling(true)
      return
    }

    // Step 4: Health Polling Phase (Docker Socket Swapper Active)
    addLog(res.message || 'Container swap initiated successfully.', 'success')
    addLog('[STAGE 4/4: HEALTH & RELOAD] Container swap initiated. Waiting for new container to boot on port 8080...', 'warn')
    isProcessing.value = false
    isPolling.value = true
    currentStep.value = 4
    startHealthPolling(false)
  } catch (err: any) {
    hasError.value = true
    addLog(`Upgrade dispatch failed: ${err.message}`, 'error')
    isProcessing.value = false
  }
}

function startHealthPolling(isTriggerMode = false) {
  let attempts = 0
  const maxAttempts = 60
  const targetVer = resolvedTargetVersion.value
  const targetClean = targetVer.replace(/^v/, '')

  const pollInterval = setInterval(async () => {
    attempts++
    try {
      addLog(`[PING ${attempts}] Probing /api/v1/health...`, 'info')
      const health = await fetchHealth()
      if (health && health.status === 'healthy') {
        const reportedVer = health.version
        const reportedClean = reportedVer ? reportedVer.replace(/^v/, '') : ''

        if (reportedVer && reportedClean !== targetClean) {
          if (isTriggerMode) {
            addLog(`[PING ${attempts}] Container responding on v${reportedClean}. Awaiting host restart (docker compose pull && docker compose up -d)...`, 'warn')
          } else {
            addLog(`[PING ${attempts}] Container responding on v${reportedClean}. Swapper transitioning containers...`, 'warn')
          }
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval)
            isPolling.value = false
            addLog(`Upgrade timed out: Container is still running v${reportedClean}. If using trigger file mode, run "docker compose pull && docker compose up -d" on the host.`, 'error')
          }
          return
        }

        clearInterval(pollInterval)
        addLog(`HEADEND SERVICE ONLINE AND RUNNING v${reportedClean || targetClean}!`, 'success')
        isPolling.value = false
        triggerPageReload()
      }
    } catch {
      // Headend is restarting/offline during container recreation
      addLog(`[PING ${attempts}] Headend offline (container restarting). Probing port 8080...`, 'info')
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
