<template>
  <div class="w-full h-full bg-gradient-to-r from-[#000055] via-[#000088] to-[#000055] border-y-2 border-[#FFFF00] flex items-center justify-between px-3 sm:px-4 font-mono text-xs sm:text-sm select-none shadow-md">
    <!-- Left: Real-time Digital Clock -->
    <div class="flex items-center space-x-2 sm:space-x-3">
      <div class="bg-[#000033] px-2.5 py-0.5 border-2 border-[#FFFF00] text-[#FFFF00] font-black tracking-widest text-sm sm:text-base md:text-lg drop-shadow">
        {{ currentTime }}
      </div>
      <span class="text-[#00FFFF] font-bold tracking-wider hidden sm:inline text-xs sm:text-sm">
        {{ currentDate }}
      </span>
    </div>

    <!-- Center: Live Open-Meteo Weather & Condition -->
    <div class="flex items-center space-x-2 sm:space-x-3 text-center truncate">
      <div class="text-[#E0E0E0] font-bold text-xs sm:text-sm md:text-base truncate">
        <span class="text-[#00FF00] font-black">{{ currentTemp }}</span> | <span class="text-[#00FFFF] uppercase font-black">{{ currentCondition }}</span>
        <span v-if="humidity !== null" class="text-[#8888AA] text-xs hidden md:inline ml-2 font-bold">
          HUMIDITY: <span class="text-[#FFFFFF]">{{ humidity }}%</span>
        </span>
        <span v-if="windSpeed !== null" class="text-[#8888AA] text-xs hidden lg:inline ml-2 font-bold">
          WIND: <span class="text-[#FFFFFF]">{{ windSpeed }}mph</span>
        </span>
      </div>
    </div>

    <!-- Right: Spotify Player Launcher, Ambient Audio & Metro Area -->
    <div class="flex items-center space-x-2 sm:space-x-3">
      <!-- Spotify Headend Audio Launcher Button -->
      <button
        type="button"
        class="bg-[#1DB954] hover:bg-[#FFFFFF] text-[#000033] px-2.5 py-0.5 sm:py-1 text-xs sm:text-sm font-black tracking-wider uppercase border border-[#1DB954] cursor-pointer shadow-[0_0_8px_rgba(29,185,84,0.6)] transition-all"
        @click="openSpotifyModal"
        title="Open Spotify Headend Audio Player"
      >
        [ SPOTIFY ]
      </button>

      <!-- Ambient Audio & Sound Controller -->
      <div class="flex items-center space-x-1.5 bg-[#000022] px-2 py-0.5 border border-[#333366]">
        <button
          @click="toggleAudio"
          class="px-2 py-0.5 text-xs font-black uppercase transition cursor-pointer"
          :class="audioSynth.isAudioActive.value ? 'bg-[#00FF00] text-[#000033]' : 'bg-[#333366] text-[#A0A0C0] hover:text-[#FFFFFF]'"
          title="Toggle Analog Tape Atmosphere & 60Hz Hum"
        >
          {{ audioSynth.isAudioActive.value ? '[ AUDIO ON ]' : '[ AUDIO MUTED ]' }}
        </button>
        <div v-if="audioSynth.isAudioActive.value" class="flex items-end space-x-0.5 h-3.5 text-[#00FF00]">
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-2"></span>
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-3.5"></span>
          <span class="w-0.5 bg-[#00FF00] animate-pulse h-2"></span>
        </div>
      </div>

      <div class="text-xs text-[#A0A0C0] hidden md:inline font-bold">
        RADIUS: <span class="text-[#FFFF00] font-black">{{ radiusMiles }}mi</span>
      </div>
      <div class="bg-[#000033] px-2.5 py-0.5 border-2 border-[#00FFFF] text-[#00FFFF] font-black tracking-wider text-xs sm:text-sm uppercase truncate max-w-[140px] sm:max-w-none">
        {{ metroLabel }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { fetchWeather } from '../api/client'
import { audioSynth } from '../services/audioSynth'
import { wsService } from '../services/websocket'
import { openSpotifyModal } from '../services/spotifyModalState'
import type { WeatherData } from '../types'

const props = withDefaults(
  defineProps<{
    metroLabel?: string
    radiusMiles?: string | number
    weatherTemp?: string
    weatherCondition?: string
  }>(),
  {
    metroLabel: 'NEW YORK CITY',
    radiusMiles: '25',
    weatherTemp: '68F',
    weatherCondition: 'CLEAR SKY',
  }
)

const currentTime = ref('')
const currentDate = ref('')
const liveWeather = ref<WeatherData | null>(null)
let clockTimer: ReturnType<typeof setInterval> | null = null
let unsubscribeWs: (() => void) | null = null

const currentTemp = computed(() => {
  if (liveWeather.value) {
    return `${Math.round(liveWeather.value.temperature)}°${liveWeather.value.temperature_unit}`
  }
  return props.weatherTemp
})

const currentCondition = computed(() => {
  if (liveWeather.value) {
    return liveWeather.value.condition
  }
  return props.weatherCondition
})

const humidity = computed(() => {
  return liveWeather.value ? liveWeather.value.humidity : null
})

const windSpeed = computed(() => {
  return liveWeather.value ? Math.round(liveWeather.value.wind_speed) : null
})

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  })
  currentDate.value = now.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  }).toUpperCase()
}

function toggleAudio() {
  audioSynth.toggleMasterAudio()
}

async function loadWeather() {
  try {
    const data = await fetchWeather()
    liveWeather.value = data
  } catch (err) {
    console.debug('Failed fetching initial live weather:', err)
  }
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  loadWeather()

  // Subscribe to live WebSocket weather updates
  unsubscribeWs = wsService.on('weather_updated', (data: WeatherData) => {
    if (data) {
      liveWeather.value = data
    }
  })
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
  if (unsubscribeWs) unsubscribeWs()
})
</script>
