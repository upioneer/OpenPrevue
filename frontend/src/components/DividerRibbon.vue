<template>
  <div class="h-[6%] w-full bg-gradient-to-r from-[#000055] via-[#000088] to-[#000055] border-y-2 border-[#FFFF00] flex items-center justify-between px-4 font-mono text-xs select-none shadow-md">
    <!-- Left: Real-time Digital Clock -->
    <div class="flex items-center space-x-3">
      <div class="bg-[#000033] px-2 py-0.5 border border-[#FFFF00] text-[#FFFF00] font-black tracking-widest text-sm drop-shadow">
        {{ currentTime }}
      </div>
      <span class="text-[#00FFFF] font-semibold tracking-wider hidden sm:inline">
        {{ currentDate }}
      </span>
    </div>

    <!-- Center: Weather & Condition -->
    <div class="flex items-center space-x-3 text-center">
      <div class="text-[#E0E0E0] font-bold">
        <span class="text-[#00FF00]">{{ weatherTemp }}</span> | <span class="text-[#00FFFF] uppercase">{{ weatherCondition }}</span>
      </div>
    </div>

    <!-- Right: Metro Area & Search Radius -->
    <div class="flex items-center space-x-3">
      <div class="text-[11px] text-[#A0A0C0] hidden md:inline">
        RADIUS: <span class="text-[#FFFF00] font-bold">{{ radiusMiles }}mi</span>
      </div>
      <div class="bg-[#000033] px-2 py-0.5 border border-[#00FFFF] text-[#00FFFF] font-bold tracking-wider text-xs">
        {{ metroLabel }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

withDefaults(
  defineProps<{
    metroLabel?: string
    radiusMiles?: string | number
    weatherTemp?: string
    weatherCondition?: string
  }>(),
  {
    metroLabel: 'NEW ORLEANS',
    radiusMiles: '35',
    weatherTemp: '74F',
    weatherCondition: 'CLEAR',
  }
)

const currentTime = ref('')
const currentDate = ref('')
let clockTimer: ReturnType<typeof setInterval> | null = null

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

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer)
})
</script>
