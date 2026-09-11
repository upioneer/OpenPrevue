<template>
  <main class="flex-1 flex flex-col w-full h-full overflow-hidden relative">
    <!-- First-Boot Setup Wizard Modal -->
    <SetupModal
      :initial-setup-completed="settings?.initial_setup_completed"
      @setup-completed="loadData"
    />

    <!-- 1. Ultrawide & Rack Bar Layout (21:9, 32:9, 10" Rack Displays 1920x480) -->
    <template v-if="isUltrawideActive">
      <!-- A. FEATURE PRIORITY: Primarily featured events/video with ONE row scrolling below -->
      <template v-if="ultrawidePriority === 'feature'">
        <!-- Top: Video or SpotlightPane fills primary display height -->
        <div class="flex-1 w-full min-h-0 overflow-hidden">
          <YouTubePane
            v-if="shouldShowYouTube"
            :source-url="settings?.youtube_source_url || ''"
            :audio-mode="settings?.youtube_audio_mode || 'mute'"
            :aspect-ratio="settings?.youtube_aspect_ratio || '4:3'"
            :shuffle-enabled="settings?.youtube_shuffle_enabled || '0'"
            :is-ultrawide="true"
            @error="handleYouTubeError"
          />
          <SpotlightPane
            v-else
            :events="events"
            :rotation-seconds="marqueeRotationSeconds"
            :is-ultrawide="true"
          />
        </div>

        <!-- Middle: Full-Width Status Ribbon -->
        <div class="h-8 sm:h-9 w-full shrink-0">
          <DividerRibbon
            :metro-label="settings?.metro_label || 'NEW YORK CITY'"
            :radius-miles="settings?.radius_miles || '25'"
          />
        </div>

        <!-- Bottom: Exactly 1 Row Scrolling Below -->
        <div class="h-[64px] sm:h-[74px] w-full shrink-0 overflow-hidden border-t-2 border-[#333366]">
          <TimelineGrid
            :venues="venues"
            :events="events"
            :scroll-speed="scrollSpeed"
            grid-density="single_row"
            :pause-duration-seconds="pauseDurationSeconds"
            :page-interval-seconds="pageIntervalSeconds"
            @ticket-toggled="handleTicketToggled"
          />
        </div>
      </template>

      <!-- B. SIDE-BY-SIDE: Desktop Dual-Pane (Split Screen for large ultrawides) -->
      <template v-else-if="ultrawidePriority === 'side_by_side'">
        <div class="h-8 sm:h-9 w-full shrink-0">
          <DividerRibbon
            :metro-label="settings?.metro_label || 'NEW YORK CITY'"
            :radius-miles="settings?.radius_miles || '25'"
          />
        </div>
        <div class="flex-1 flex flex-row w-full min-h-0 overflow-hidden">
          <div class="w-1/2 h-full shrink-0 overflow-hidden">
            <YouTubePane
              v-if="shouldShowYouTube"
              :source-url="settings?.youtube_source_url || ''"
              :audio-mode="settings?.youtube_audio_mode || 'mute'"
              :aspect-ratio="settings?.youtube_aspect_ratio || '4:3'"
              :shuffle-enabled="settings?.youtube_shuffle_enabled || '0'"
              :is-ultrawide="true"
              @error="handleYouTubeError"
            />
            <SpotlightPane
              v-else
              :events="events"
              :rotation-seconds="marqueeRotationSeconds"
              :is-ultrawide="true"
            />
          </div>
          <div class="w-[3px] bg-[#333366] border-x border-[#FFFF00] h-full shrink-0 shadow-[0_0_8px_rgba(255,255,0,0.6)]"></div>
          <div class="flex-1 h-full overflow-hidden">
            <TimelineGrid
              :venues="venues"
              :events="events"
              :scroll-speed="scrollSpeed"
              :grid-density="gridDensity"
              :pause-duration-seconds="pauseDurationSeconds"
              :page-interval-seconds="pageIntervalSeconds"
              @ticket-toggled="handleTicketToggled"
            />
          </div>
        </div>
      </template>

      <!-- C. CALENDAR PRIORITY (DEFAULT): NO featured events at all, 100% full-screen schedule grid -->
      <template v-else>
        <!-- Top Status Ribbon -->
        <div class="h-8 sm:h-9 w-full shrink-0">
          <DividerRibbon
            :metro-label="settings?.metro_label || 'NEW YORK CITY'"
            :radius-miles="settings?.radius_miles || '25'"
          />
        </div>

        <!-- 100% Full-Screen Scrolling Schedule Grid (No Featured Events Displayed) -->
        <div class="flex-1 w-full min-h-0 overflow-hidden">
          <TimelineGrid
            :venues="venues"
            :events="events"
            :scroll-speed="scrollSpeed"
            :grid-density="gridDensity"
            :pause-duration-seconds="pauseDurationSeconds"
            :page-interval-seconds="pageIntervalSeconds"
            @ticket-toggled="handleTicketToggled"
          />
        </div>
      </template>
    </template>

    <!-- 2. Classic 16:9 / 4:3 Vertically Stacked Presentation -->
    <template v-else>
      <!-- Top Pane: Video Stream or Spotlight Promo (Expands to flex-1 if single_row, otherwise 45% Landscape / 34% Portrait) -->
      <div
        class="w-full shrink-0 overflow-hidden"
        :class="gridDensity === 'single_row'
          ? 'flex-1 min-h-0'
          : 'h-[45%] portrait-spotlight-height'"
      >
        <YouTubePane
          v-if="shouldShowYouTube"
          :source-url="settings?.youtube_source_url || ''"
          :audio-mode="settings?.youtube_audio_mode || 'mute'"
          :aspect-ratio="settings?.youtube_aspect_ratio || '4:3'"
          :shuffle-enabled="settings?.youtube_shuffle_enabled || '0'"
          @error="handleYouTubeError"
        />
        <SpotlightPane
          v-else
          :events="events"
          :rotation-seconds="marqueeRotationSeconds"
        />
      </div>

      <!-- Middle Ribbon: Divider Status Bar (h-8/h-9 for single_row, or 6% Landscape / 5% Portrait) -->
      <div
        class="w-full shrink-0"
        :class="gridDensity === 'single_row'
          ? 'h-8 sm:h-9'
          : 'h-[6%] portrait-ribbon-height'"
      >
        <DividerRibbon
          :metro-label="settings?.metro_label || 'NEW YORK CITY'"
          :radius-miles="settings?.radius_miles || '25'"
        />
      </div>

      <!-- Bottom Pane: Scrolling Timeline Grid (h-[64px]/h-[74px] for single_row, or 49% Landscape / 61% Portrait) -->
      <div
        class="w-full overflow-hidden"
        :class="gridDensity === 'single_row'
          ? 'h-[64px] sm:h-[74px] shrink-0 border-t-2 border-[#333366]'
          : 'h-[49%] portrait-grid-height flex-1'"
      >
        <TimelineGrid
          :venues="venues"
          :events="events"
          :scroll-speed="scrollSpeed"
          :grid-density="gridDensity"
          :pause-duration-seconds="pauseDurationSeconds"
          :page-interval-seconds="pageIntervalSeconds"
          @ticket-toggled="handleTicketToggled"
        />
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import SpotlightPane from '../components/SpotlightPane.vue'
import YouTubePane from '../components/YouTubePane.vue'
import DividerRibbon from '../components/DividerRibbon.vue'
import TimelineGrid from '../components/TimelineGrid.vue'
import SetupModal from '../components/SetupModal.vue'
import { fetchEvents, fetchSettings, fetchVenues } from '../api/client'
import { wsService } from '../services/websocket'
import { wakeLockService } from '../services/wakeLock'
import type { EventItem, SystemSettings, VenueItem } from '../types'

const events = ref<EventItem[]>([])
const venues = ref<VenueItem[]>([])
const settings = ref<SystemSettings | null>(null)
const isUltrawideDetected = ref(false)
const youtubeError = ref(false)
let refreshInterval: ReturnType<typeof setInterval> | null = null
let unsubscribeEventsWs: (() => void) | null = null
let unsubscribeSettingsWs: (() => void) | null = null

function checkUltrawideRatio() {
  if (typeof window !== 'undefined') {
    const screenRatio = window.screen && window.screen.height > 0
      ? window.screen.width / window.screen.height
      : 0
    const viewportRatio = window.innerHeight > 0
      ? window.innerWidth / window.innerHeight
      : 0

    // Standard 16:9 (1.78:1), 16:10 (1.60:1), and 4:3 (1.33:1) displays.
    // Desktop browsers on 16:9 screens have viewportRatio ~2.0 - 2.15 due to browser chrome/taskbars.
    // That must NEVER falsely trigger ultrawide mode.
    // True ultrawide monitors (21:9 is ~2.37:1, 32:9 is ~3.55:1) and rack consoles (1920x480 is 4.0:1).
    if (screenRatio > 0 && screenRatio < 2.2) {
      isUltrawideDetected.value = viewportRatio >= 2.35
    } else {
      isUltrawideDetected.value = screenRatio >= 2.2 || viewportRatio >= 2.35
    }
  }
}

const isUltrawideActive = computed(() => {
  const mode = settings.value?.ultrawide_mode || 'auto'
  if (mode === 'always') return true
  if (mode === 'disabled') return false
  return isUltrawideDetected.value
})

const ultrawidePriority = computed(() => {
  return settings.value?.ultrawide_priority || 'feature'
})

const marqueeRotationSeconds = computed(() => {
  if (!settings.value?.marquee_rotation_seconds) return 20
  return parseInt(settings.value.marquee_rotation_seconds, 10) || 20
})

const scrollSpeed = computed(() => {
  if (!settings.value?.autoscroll_speed) return 30
  return parseInt(settings.value.autoscroll_speed, 10) || 30
})

const gridDensity = computed(() => {
  return settings.value?.grid_density || 'balanced'
})

const pauseDurationSeconds = computed(() => {
  if (!settings.value?.scroll_pause_duration) return 4
  return parseInt(settings.value.scroll_pause_duration, 10) || 4
})

const pageIntervalSeconds = computed(() => {
  if (!settings.value?.scroll_page_interval) return 6
  return parseInt(settings.value.scroll_page_interval, 10) || 6
})

const shouldShowYouTube = computed(() => {
  return (
    settings.value?.spotlight_mode === 'youtube' &&
    !!settings.value?.youtube_source_url?.trim() &&
    !youtubeError.value
  )
})

function handleYouTubeError(code: number) {
  console.warn('YouTube player error:', code, 'Falling back to Featured Events Showcase.')
  youtubeError.value = true
}

watch(
  () => settings.value?.youtube_source_url,
  () => {
    youtubeError.value = false
  }
)

watch(
  () => settings.value?.spotlight_mode,
  () => {
    youtubeError.value = false
  }
)

async function loadData() {
  try {
    const [fetchedEvents, fetchedVenues, fetchedSettings] = await Promise.all([
      fetchEvents({ status: 'active', limit: 200 }),
      fetchVenues(),
      fetchSettings(),
    ])
    events.value = fetchedEvents
    venues.value = fetchedVenues
    settings.value = fetchedSettings

    if (fetchedSettings.screen_wake_lock_enabled !== '0') {
      wakeLockService.requestWakeLock()
    }
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
  }
}

function handleTicketToggled(eventId: string, hasTicket: number) {
  const target = events.value.find((e) => e.id === eventId)
  if (target) {
    target.has_ticket = hasTicket
  }
}

onMounted(() => {
  checkUltrawideRatio()
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', checkUltrawideRatio)
  }

  loadData()
  // Refresh fallback data every 60 seconds
  refreshInterval = setInterval(loadData, 60000)

  // Real-time WebSocket updates
  unsubscribeEventsWs = wsService.on('events_updated', () => {
    loadData()
  })

  unsubscribeSettingsWs = wsService.on('settings_updated', () => {
    loadData()
  })
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', checkUltrawideRatio)
  }
  if (refreshInterval) clearInterval(refreshInterval)
  if (unsubscribeEventsWs) unsubscribeEventsWs()
  if (unsubscribeSettingsWs) unsubscribeSettingsWs()
})
</script>
