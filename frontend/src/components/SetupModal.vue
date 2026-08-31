<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 select-none font-mono"
  >
    <div
      class="w-full max-w-2xl bg-gradient-to-b from-[#000088] via-[#000055] to-[#000022] border-2 border-[#FFFF00] rounded-xs shadow-[0_0_24px_rgba(255,255,0,0.5)] overflow-hidden max-h-[90vh] flex flex-col"
    >
      <!-- Top Title Bar -->
      <div class="bg-[#0000AA] border-b-2 border-[#FFFF00] px-4 py-2 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 bg-[#FFFF00] inline-block animate-pulse"></span>
          <span class="text-sm font-black text-[#FFFF00] tracking-widest">
            [ OPENPREVUE SETUP WIZARD ]
          </span>
        </div>
        <span class="text-xs text-[#00FFFF]">FIRST BOOT INITIALIZATION</span>
      </div>

      <!-- Content Area -->
      <div class="p-4 sm:p-6 space-y-4 text-xs overflow-y-auto">
        <div class="bg-[#000033] border border-[#333366] p-3 text-[#E0E0E0] leading-relaxed">
          <span class="text-[#FFFF00] font-bold block mb-1">WELCOME TO OPENPREVUE 1990S TV GUIDE</span>
          Select your local broadcasting area below. You can pick an instant city preset or enter your custom city name and postal code.
        </div>

        <!-- Quick City Presets -->
        <div>
          <label class="block text-[#00FFFF] font-bold uppercase mb-2">QUICK REGIONAL PRESETS:</label>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-1.5">
            <button
              v-for="preset in REGIONAL_PRESETS"
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

        <!-- Custom Fields & Geocoding Resolver -->
        <div class="space-y-3 pt-2 border-t border-[#333366]">
          <div class="flex items-center justify-between">
            <label class="block text-[#00FFFF] font-bold uppercase">CUSTOM CITY OR POSTAL CODE LOOKUP:</label>
            <span v-if="isGeocoding" class="text-[#FFFF00] animate-pulse font-bold">[ LOCATING... ]</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-[#8888AA] font-bold mb-1">CITY / CHANNEL BROADCAST LABEL:</label>
              <div class="flex space-x-1">
                <input
                  v-model="metroLabel"
                  type="text"
                  class="flex-1 bg-[#000022] border border-[#333366] text-[#FFFF00] font-bold px-2 py-1 uppercase focus:border-[#FFFF00] outline-hidden"
                  placeholder="e.g. AUSTIN, TX"
                  @blur="handleAutoGeocode(metroLabel)"
                  @keydown.enter.prevent="handleAutoGeocode(metroLabel)"
                />
                <button
                  type="button"
                  class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-2 py-1 text-[10px] font-bold cursor-pointer transition-colors"
                  @click="handleAutoGeocode(metroLabel)"
                >
                  [ RESOLVE ]
                </button>
              </div>
            </div>

            <div>
              <label class="block text-[#8888AA] font-bold mb-1">POSTAL / ZIP CODE:</label>
              <div class="flex space-x-1">
                <input
                  v-model="postalCode"
                  type="text"
                  class="flex-1 bg-[#000022] border border-[#333366] text-[#FFFF00] font-bold px-2 py-1 focus:border-[#FFFF00] outline-hidden"
                  placeholder="e.g. 78701"
                  @blur="handleAutoGeocode(postalCode)"
                  @keydown.enter.prevent="handleAutoGeocode(postalCode)"
                />
                <button
                  type="button"
                  class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-2 py-1 text-[10px] font-bold cursor-pointer transition-colors"
                  @click="handleAutoGeocode(postalCode)"
                >
                  [ RESOLVE ]
                </button>
              </div>
            </div>

            <div>
              <label class="block text-[#8888AA] font-bold mb-1">RESOLVED COORDINATES (LAT / LON):</label>
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

          <div v-if="geocodeMessage" class="p-2 border text-xs" :class="geocodeIsError ? 'bg-[#330000] border-[#FF4444] text-[#FF8888]' : 'bg-[#003300] border-[#00FF00] text-[#00FF00] font-bold'">
            {{ geocodeMessage }}
          </div>
        </div>

        <!-- Audio Atmosphere Opt-In Toggle -->
        <div class="bg-[#000033] p-3 border border-[#00FFFF] space-y-1">
          <label class="flex items-center space-x-2 text-xs font-bold text-[#00FFFF] cursor-pointer">
            <input
              v-model="enableAudioOnBoot"
              type="checkbox"
              class="w-4 h-4 accent-[#00FF00]"
            />
            <span>Enable 1990s Analog Tape Hiss & CRT Atmosphere Automatically</span>
          </label>
          <p class="text-[10px] text-[#8888AA] pl-6">
            Plays subtle analog tape atmosphere through the 12 kHz CRT filter when you start the guide.
          </p>
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
import { geocodeLocationQuery, refreshWeather, triggerSync, updateSetting } from '../api/client'
import { REGIONAL_PRESETS, type RegionalPreset } from '../services/regionalPresets'
import { audioSynth } from '../services/audioSynth'

const props = defineProps<{
  initialSetupCompleted?: string
}>()

const emit = defineEmits<{
  (e: 'setup-completed'): void
}>()

const isOpen = ref(false)
const isSaving = ref(false)
const selectedPreset = ref('NYC')
const enableAudioOnBoot = ref(true)

const metroLabel = ref('NEW YORK CITY')
const postalCode = ref('10001')
const latitude = ref('40.7128')
const longitude = ref('-74.0060')
const radiusMiles = ref('25')

const isGeocoding = ref(false)
const geocodeMessage = ref('')
const geocodeIsError = ref(false)

function applyPreset(preset: RegionalPreset) {
  selectedPreset.value = preset.label
  metroLabel.value = preset.metro
  postalCode.value = preset.zip
  latitude.value = preset.lat.toString()
  longitude.value = preset.lon.toString()
  radiusMiles.value = preset.radius.toString()
  geocodeMessage.value = `[PRESET SELECTED] ${preset.metro} (${preset.lat}, ${preset.lon})`
  geocodeIsError.value = false
}

async function handleAutoGeocode(query: string) {
  if (!query || query.trim().length < 2) return
  isGeocoding.value = true
  geocodeMessage.value = ''
  geocodeIsError.value = false

  try {
    const results = await geocodeLocationQuery(query.trim())
    if (results && results.length > 0) {
      const match = results[0]
      metroLabel.value = match.metro_label
      if (match.postal_code) {
        postalCode.value = match.postal_code
      }
      latitude.value = match.latitude.toString()
      longitude.value = match.longitude.toString()
      selectedPreset.value = ''
      geocodeMessage.value = `LOCATION RESOLVED: ${match.display_label} (${match.latitude.toFixed(4)}, ${match.longitude.toFixed(4)})`
    } else {
      geocodeIsError.value = true
      geocodeMessage.value = `Could not auto-locate "${query}". You may enter coordinates manually.`
    }
  } catch (err) {
    geocodeIsError.value = true
    geocodeMessage.value = `Geocoding error: ${String(err)}`
  } finally {
    isGeocoding.value = false
  }
}

async function saveAndInitialize() {
  isSaving.value = true
  try {
    // If coordinates were not resolved yet for custom input, try resolving first
    if (metroLabel.value && (latitude.value === '40.7128' && longitude.value === '-74.0060' && metroLabel.value !== 'NEW YORK CITY')) {
      try {
        const results = await geocodeLocationQuery(metroLabel.value)
        if (results && results.length > 0) {
          latitude.value = results[0].latitude.toString()
          longitude.value = results[0].longitude.toString()
          if (results[0].postal_code) postalCode.value = results[0].postal_code
        }
      } catch {
        // Continue with current values
      }
    }

    await updateSetting('metro_label', metroLabel.value)
    await updateSetting('postal_code', postalCode.value)
    await updateSetting('latitude', latitude.value)
    await updateSetting('longitude', longitude.value)
    await updateSetting('radius_miles', radiusMiles.value)
    await updateSetting('initial_setup_completed', '1')

    // Refresh weather immediately for new location
    refreshWeather().catch(() => {})

    audioSynth.setAutoPlayOptIn(enableAudioOnBoot.value)
    if (enableAudioOnBoot.value) {
      audioSynth.startTurnkeyAudio()
    }

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

  audioSynth.setAutoPlayOptIn(enableAudioOnBoot.value)
  if (enableAudioOnBoot.value) {
    audioSynth.startTurnkeyAudio()
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
