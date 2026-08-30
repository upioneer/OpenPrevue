<template>
  <div class="flex-1 overflow-y-auto p-6 bg-[#000033] font-mono text-[#E0E0E0] select-none">
    <div class="max-w-3xl mx-auto space-y-6">
      <!-- Title Header -->
      <div class="border-b-2 border-[#FFFF00] pb-3 flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-[#FFFF00] tracking-wider">SYSTEM CONFIGURATION // SETTINGS</h1>
          <p class="text-xs text-[#8888AA]">Dynamic SQLite parameters applied without container restarts</p>
        </div>
        <button
          :disabled="isSyncing"
          class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-3 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
          @click="handleManualSync"
        >
          {{ isSyncing ? '[ SYNCING... ]' : '[ SYNC PROVIDERS NOW ]' }}
        </button>
      </div>

      <!-- Notification Banner -->
      <div v-if="saveMessage" class="bg-[#000055] border border-[#00FF00] text-[#00FF00] px-4 py-2 text-xs">
        {{ saveMessage }}
      </div>

      <!-- Settings Form -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Location & Radius Section -->
        <div class="bg-[#000044] p-4 border border-[#333366] space-y-4">
          <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
            Location & Discovery
          </h2>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Postal Code (ZIP):</label>
            <input
              v-model="form.postal_code"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Metro Area Label:</label>
            <input
              v-model="form.metro_label"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Search Radius: {{ form.radius_miles }} miles</label>
            <input
              v-model="form.radius_miles"
              type="range"
              min="5"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[10px] text-[#A0A0C0] block">Latitude:</label>
              <input
                v-model="form.latitude"
                type="text"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
            <div>
              <label class="text-[10px] text-[#A0A0C0] block">Longitude:</label>
              <input
                v-model="form.longitude"
                type="text"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
          </div>
        </div>

        <!-- Display & Animation Controls -->
        <div class="bg-[#000044] p-4 border border-[#333366] space-y-4">
          <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
            Display & Visuals
          </h2>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Autoscroll Speed: {{ form.autoscroll_speed }} px/sec</label>
            <input
              v-model="form.autoscroll_speed"
              type="range"
              min="20"
              max="180"
              step="10"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Spotlight Rotation: {{ form.marquee_rotation_seconds }}s</label>
            <input
              v-model="form.marquee_rotation_seconds"
              type="range"
              min="10"
              max="60"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="space-y-2 pt-2 border-t border-[#333366]">
            <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
              <input
                type="checkbox"
                :checked="form.scanline_intensity !== '0'"
                class="accent-[#00FFFF]"
                @change="toggleScanlines"
              />
              <span>Enable CRT Scanline Shader Overlay</span>
            </label>

            <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
              <input
                type="checkbox"
                :checked="form.phosphor_glow === '1'"
                class="accent-[#00FFFF]"
                @change="toggleGlow"
              />
              <span>Enable Retro Phosphor Bloom Effect</span>
            </label>

            <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
              <input
                type="checkbox"
                :checked="form.crt_curvature === '1'"
                class="accent-[#00FFFF]"
                @change="toggleCurvature"
              />
              <span>Enable CRT Screen Curvature Vignette</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-end space-x-4 pt-4 border-t border-[#333366]">
        <router-link
          to="/"
          class="px-4 py-2 border border-[#8888AA] text-[#8888AA] hover:text-[#FFFFFF] text-xs font-bold uppercase transition-colors"
        >
          Back to Guide
        </router-link>
        <button
          class="bg-[#FFFF00] text-[#000033] px-6 py-2 text-xs font-black uppercase hover:bg-[#FFFF77] transition-colors cursor-pointer shadow"
          @click="saveAllSettings"
        >
          Save All Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { fetchSettings, triggerSync, updateSetting } from '../api/client'
import type { SystemSettings } from '../types'

const isSyncing = ref(false)
const saveMessage = ref('')

const form = reactive<SystemSettings>({
  postal_code: '70112',
  metro_label: 'NEW ORLEANS',
  latitude: '29.9511',
  longitude: '-90.0715',
  radius_miles: '35',
  autoscroll_speed: '60',
  marquee_rotation_seconds: '20',
  scanline_intensity: '8',
  phosphor_glow: '1',
  crt_curvature: '0',
  vhs_tracking_noise: '0',
  time_format: '12h',
  sync_interval_hours: '6',
})

async function loadSettings() {
  try {
    const s = await fetchSettings()
    Object.assign(form, s)
  } catch (err) {
    console.error('Failed to load settings:', err)
  }
}

function toggleScanlines(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  form.scanline_intensity = checked ? '8' : '0'
}

function toggleGlow(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  form.phosphor_glow = checked ? '1' : '0'
}

function toggleCurvature(e: Event) {
  const checked = (e.target as HTMLInputElement).checked
  form.crt_curvature = checked ? '1' : '0'
}

async function saveAllSettings() {
  try {
    for (const [k, v] of Object.entries(form)) {
      await updateSetting(k, String(v))
    }
    saveMessage.value = 'SUCCESS: Settings saved and applied to system datastore.'
    setTimeout(() => {
      saveMessage.value = ''
    }, 4000)
  } catch (err) {
    saveMessage.value = `ERROR: Failed to save settings: ${String(err)}`
  }
}

async function handleManualSync() {
  isSyncing.value = true
  try {
    const res = await triggerSync()
    saveMessage.value = `SYNC: ${res.message}`
    setTimeout(() => {
      saveMessage.value = ''
    }, 4000)
  } catch (err) {
    saveMessage.value = `ERROR: Sync failed: ${String(err)}`
  } finally {
    isSyncing.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
