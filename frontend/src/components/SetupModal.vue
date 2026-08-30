<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 select-none font-mono"
  >
    <div
      class="w-full max-w-xl bg-gradient-to-b from-[#000088] via-[#000055] to-[#000022] border-2 border-[#FFFF00] rounded-xs shadow-[0_0_24px_rgba(255,255,0,0.5)] overflow-hidden"
    >
      <!-- Top Title Bar -->
      <div class="bg-[#0000AA] border-b-2 border-[#FFFF00] px-4 py-2 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 bg-[#FFFF00] inline-block animate-pulse"></span>
          <span class="text-sm font-black text-[#FFFF00] tracking-widest">
            [ OPENPREVUE SETUP WIZARD ]
          </span>
        </div>
        <span class="text-xs text-[#00FFFF]">FIRST BOOT INITIALIZATION</span>
      </div>

      <!-- Content Area -->
      <div class="p-4 sm:p-6 space-y-4 text-xs">
        <div class="bg-[#000033] border border-[#333366] p-3 text-[#E0E0E0] leading-relaxed">
          <span class="text-[#FFFF00] font-bold block mb-1">WELCOME TO OPENPREVUE 1990S TV GUIDE</span>
          Select your local broadcasting area below. You can pick an instant city preset or enter your custom city name and postal code.
        </div>

        <!-- Quick City Presets -->
        <div>
          <label class="block text-[#00FFFF] font-bold uppercase mb-2">QUICK REGIONAL PRESETS:</label>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <button
              v-for="preset in presets"
              :key="preset.label"
              type="button"
              class="px-2 py-1.5 border text-[11px] font-bold transition-all text-left truncate cursor-pointer"
              :class="selectedPreset === preset.label
                ? 'bg-[#FFFF00] text-[#000033] border-[#FFFF00] shadow-[0_0_8px_rgba(255,255,0,0.8)]'
                : 'bg-[#000044] text-[#E0E0E0] border-[#333366] hover:border-[#00FFFF] hover:text-[#00FFFF]'"
              @click="applyPreset(preset)"
            >
              [ {{ preset.label }} ]
            </button>
          </div>
        </div>

        <!-- Custom Fields -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-[#333366]">
          <div>
            <label class="block text-[#8888AA] font-bold mb-1">METRO / CHANNEL LABEL:</label>
            <input
              v-model="metroLabel"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] text-[#FFFF00] font-bold px-2 py-1 uppercase focus:border-[#FFFF00] outline-hidden"
              placeholder="e.g. NEW YORK CITY"
            />
          </div>

          <div>
            <label class="block text-[#8888AA] font-bold mb-1">POSTAL / ZIP CODE:</label>
            <input
              v-model="postalCode"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] text-[#FFFF00] font-bold px-2 py-1 focus:border-[#FFFF00] outline-hidden"
              placeholder="e.g. 10001"
            />
          </div>

          <div>
            <label class="block text-[#8888AA] font-bold mb-1">LATITUDE / LONGITUDE:</label>
            <div class="flex space-x-1">
              <input
                v-model="latitude"
                type="text"
                class="w-1/2 bg-[#000022] border border-[#333366] text-[#E0E0E0] px-2 py-1 text-[11px] focus:border-[#00FFFF] outline-hidden"
                placeholder="Lat"
              />
              <input
                v-model="longitude"
                type="text"
                class="w-1/2 bg-[#000022] border border-[#333366] text-[#E0E0E0] px-2 py-1 text-[11px] focus:border-[#00FFFF] outline-hidden"
                placeholder="Lon"
              />
            </div>
          </div>

          <div>
            <label class="block text-[#8888AA] font-bold mb-1">DISCOVERY RADIUS (MILES):</label>
            <input
              v-model="radiusMiles"
              type="number"
              class="w-full bg-[#000022] border border-[#333366] text-[#E0E0E0] px-2 py-1 text-[11px] focus:border-[#00FFFF] outline-hidden"
              placeholder="25"
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-2 pt-3 border-t border-[#FFFF00]/50">
          <button
            type="button"
            class="w-full sm:w-auto px-4 py-2 bg-[#000044] border border-[#333366] text-[#8888AA] hover:text-[#FFFFFF] hover:border-[#8888AA] font-bold cursor-pointer transition-all"
            @click="dismissDefault"
          >
            [ KEEP DEFAULT NYC ]
          </button>

          <button
            type="button"
            class="w-full sm:w-auto px-6 py-2 bg-[#FFFF00] text-[#000033] border-2 border-[#FFFF00] font-black hover:bg-[#FFFFFF] cursor-pointer shadow-[0_0_12px_rgba(255,255,0,0.8)] transition-all"
            :disabled="isSaving"
            @click="saveAndInitialize"
          >
            {{ isSaving ? '[ INITIALIZING... ]' : '[ INITIALIZE PREVUE CHANNEL ]' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { triggerSync, updateSetting } from '../api/client'

const props = defineProps<{
  initialSetupCompleted?: string
}>()

const emit = defineEmits<{
  (e: 'setup-completed'): void
}>()

const isOpen = ref(false)
const isSaving = ref(false)
const selectedPreset = ref('NYC')

const presets = [
  { label: 'NYC', metro: 'NEW YORK CITY', zip: '10001', lat: 40.7128, lon: -74.0060, radius: 25 },
  { label: 'LOS ANGELES', metro: 'LOS ANGELES', zip: '90012', lat: 34.0522, lon: -118.2437, radius: 30 },
  { label: 'CHICAGO', metro: 'CHICAGO', zip: '60601', lat: 41.8781, lon: -87.6298, radius: 25 },
  { label: 'AUSTIN', metro: 'AUSTIN', zip: '78701', lat: 30.2672, lon: -97.7431, radius: 25 },
  { label: 'SEATTLE', metro: 'SEATTLE', zip: '98101', lat: 47.6062, lon: -122.3321, radius: 25 },
  { label: 'LONDON', metro: 'LONDON', zip: 'EC1A 1BB', lat: 51.5074, lon: -0.1278, radius: 20 },
]

const metroLabel = ref('NEW YORK CITY')
const postalCode = ref('10001')
const latitude = ref('40.7128')
const longitude = ref('-74.0060')
const radiusMiles = ref('25')

function applyPreset(preset: typeof presets[0]) {
  selectedPreset.value = preset.label
  metroLabel.value = preset.metro
  postalCode.value = preset.zip
  latitude.value = preset.lat.toString()
  longitude.value = preset.lon.toString()
  radiusMiles.value = preset.radius.toString()
}

async function saveAndInitialize() {
  isSaving.value = true
  try {
    await updateSetting('metro_label', metroLabel.value)
    await updateSetting('postal_code', postalCode.value)
    await updateSetting('latitude', latitude.value)
    await updateSetting('longitude', longitude.value)
    await updateSetting('radius_miles', radiusMiles.value)
    await updateSetting('initial_setup_completed', '1')

    localStorage.setItem('openprevue_onboarded', '1')
    isOpen.value = false
    emit('setup-completed')

    // Trigger immediate background sync
    triggerSync().catch(() => {})
  } catch (err) {
    console.error('Failed to save initial setup settings:', err)
  } finally {
    isSaving.value = false
  }
}

async function dismissDefault() {
  try {
    await updateSetting('initial_setup_completed', '1')
  } catch {
    // Ignore
  }
  localStorage.setItem('openprevue_onboarded', '1')
  isOpen.value = false
  emit('setup-completed')
}

onMounted(() => {
  const localOnboarded = localStorage.getItem('openprevue_onboarded')
  if (!localOnboarded && props.initialSetupCompleted !== '1') {
    isOpen.value = true
  }
})
</script>
