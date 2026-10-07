<template>
  <div class="w-full h-full flex flex-row min-h-0 overflow-hidden">
    <!-- Left: persistent event showcase, never interrupted -->
    <div data-testid="split-showcase" class="flex-1 h-full min-w-0 min-h-0 overflow-hidden relative">
      <SpotlightPane
        :events="events"
        :rotation-seconds="rotationSeconds"
        :is-ultrawide="isUltrawide"
      />
    </div>

    <!-- Center: retro channel divider -->
    <div class="w-[3px] bg-[#333366] border-x border-[#FFFF00] h-full shrink-0 shadow-[0_0_8px_rgba(255,255,0,0.6)]"></div>

    <!-- Right: retro ad break interruption -->
    <div data-testid="split-ad" class="flex-1 h-full min-w-0 min-h-0 overflow-hidden relative">
      <YouTubePane
        v-if="commercialType === 'youtube'"
        :source-url="sourceUrl"
        audio-mode="audio"
        :aspect-ratio="aspectRatio"
        shuffle-enabled="1"
        :is-ultrawide="isUltrawide"
        :is-commercial-break="true"
        @error="emit('error', $event)"
        @commercial-finished="emit('commercialFinished')"
      />
      <div
        v-else
        class="w-full h-full bg-black flex items-center justify-center relative"
      >
        <video
          :src="commercialUrl"
          autoplay
          class="max-w-full max-h-full"
          @ended="emit('commercialFinished')"
          @error="emit('commercialFinished')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import SpotlightPane from './SpotlightPane.vue'
import YouTubePane from './YouTubePane.vue'
import type { EventItem } from '../types'

withDefaults(
  defineProps<{
    events: EventItem[]
    rotationSeconds: number
    isUltrawide?: boolean
    sourceUrl: string
    aspectRatio?: string
    commercialType?: 'youtube' | 'local' | string
    commercialUrl?: string
  }>(),
  {
    isUltrawide: false,
    aspectRatio: '4:3',
    commercialType: 'youtube',
    commercialUrl: '',
  }
)

const emit = defineEmits<{
  (e: 'error', code: number): void
  (e: 'commercialFinished'): void
}>()
</script>
