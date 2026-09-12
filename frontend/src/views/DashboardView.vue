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
            :audio-mode="youtubeAudioMode"
            :aspect-ratio="youtubeAspectRatio"
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
            :grid-filter-mode="gridFilterMode"
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
              :audio-mode="youtubeAudioMode"
              :aspect-ratio="youtubeAspectRatio"
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
              :grid-filter-mode="gridFilterMode"
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
            :grid-filter-mode="gridFilterMode"
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
          :audio-mode="youtubeAudioMode"
          :aspect-ratio="youtubeAspectRatio"
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
          :grid-filter-mode="gridFilterMode"
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
import { useRoute } from 'vue-router'
import { audioSynth } from '../services/audioSynth'
import SpotlightPane from '../components/SpotlightPane.vue'
import YouTubePane from '../components/YouTubePane.vue'
import DividerRibbon from '../components/DividerRibbon.vue'
import TimelineGrid from '../components/TimelineGrid.vue'
import SetupModal from '../components/SetupModal.vue'
import { fetchEvents, fetchSettings, fetchVenues } from '../api/client'
import { wsService } from '../services/websocket'
import { wakeLockService } from '../services/wakeLock'
import type { EventItem, SystemSettings, VenueItem } from '../types'

const route = useRoute()
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
  const queryUltrawide = route.query.ultrawide
  if (queryUltrawide === '1' || queryUltrawide === 'true' || queryUltrawide === 'always') return true
  if (queryUltrawide === '0' || queryUltrawide === 'false' || queryUltrawide === 'disabled') return false

  const mode = settings.value?.ultrawide_mode || 'auto'
  if (mode === 'always') return true
  if (mode === 'disabled') return false
  return isUltrawideDetected.value
})

const ultrawidePriority = computed(() => {
  const queryPriority = route.query.priority
  if (typeof queryPriority === 'string') {
    const p = queryPriority.toLowerCase()
    if (['feature', 'side_by_side'].includes(p)) return p
  }
  return settings.value?.ultrawide_priority || 'feature'
})

const marqueeRotationSeconds = computed(() => {
  const queryRotation = route.query.rotation
  if (typeof queryRotation === 'string') {
    const r = parseInt(queryRotation, 10)
    if (!isNaN(r) && r >= 5 && r <= 120) return r
  }
  if (!settings.value?.marquee_rotation_seconds) return 20
  return parseInt(settings.value.marquee_rotation_seconds, 10) || 20
})

const scrollSpeed = computed(() => {
  const querySpeed = route.query.speed
  if (typeof querySpeed === 'string') {
    const s = parseInt(querySpeed, 10)
    if (!isNaN(s) && s >= 10 && s <= 120) return s
  }
  if (!settings.value?.autoscroll_speed) return 30
  return parseInt(settings.value.autoscroll_speed, 10) || 30
})

const gridDensity = computed(() => {
  const queryDensity = route.query.density
  if (typeof queryDensity === 'string') {
    const d = queryDensity.toLowerCase()
    if (['classic_tv', 'balanced', 'dense', 'single_row'].includes(d)) {
      return d
    }
  }
  return settings.value?.grid_density || 'balanced'
})

const gridFilterMode = computed(() => {
  const queryFilter = route.query.filter || route.query.listings || route.query.active_only
  if (typeof queryFilter === 'string') {
    const f = queryFilter.toLowerCase()
    if (['all', '0', 'false'].includes(f)) return 'all'
    if (['active', 'active_only', '1', 'true'].includes(f)) return 'active_only'
  }
  return settings.value?.grid_filter_mode || 'active_only'
})

const pauseDurationSeconds = computed(() => {
  const queryPause = route.query.pause
  if (typeof queryPause === 'string') {
    const p = parseInt(queryPause, 10)
    if (!isNaN(p) && p >= 0 && p <= 60) return p
  }
  if (!settings.value?.scroll_pause_duration) return 4
  return parseInt(settings.value.scroll_pause_duration, 10) || 4
})

const pageIntervalSeconds = computed(() => {
  if (!settings.value?.scroll_page_interval) return 6
  return parseInt(settings.value.scroll_page_interval, 10) || 6
})

const shouldShowYouTube = computed(() => {
  const queryVideo = route.query.video
  if (queryVideo === '0' || queryVideo === 'off' || queryVideo === 'spotlight') return false
  if (queryVideo === '1' || queryVideo === 'youtube') {
    return !!settings.value?.youtube_source_url?.trim() && !youtubeError.value
  }

  return (
    settings.value?.spotlight_mode === 'youtube' &&
    !!settings.value?.youtube_source_url?.trim() &&
    !youtubeError.value
  )
})

const youtubeAudioMode = computed(() => {
  const queryAudio = route.query.audio
  if (queryAudio === '1' || queryAudio === 'on' || queryAudio === 'audio') return 'audio'
  if (queryAudio === '0' || queryAudio === 'off' || queryAudio === 'mute') return 'mute'
  return settings.value?.youtube_audio_mode || 'mute'
})

const youtubeAspectRatio = computed(() => {
  const queryAspect = route.query.aspect || route.query.ratio
  if (typeof queryAspect === 'string') {
    const a = queryAspect.toLowerCase()
    if (['4:3', '16:9', 'stretch', 'auto'].includes(a)) return a
  }
  return settings.value?.youtube_aspect_ratio || '4:3'
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

  // Process URL query overrides for client-specific volume and mute
  const queryVol = route.query.volume
  if (typeof queryVol === 'string') {
    const parsedVol = parseInt(queryVol, 10)
    if (!isNaN(parsedVol) && parsedVol >= 0 && parsedVol <= 100) {
      audioSynth.setMasterVolume(parsedVol)
    }
  }
  const queryAudio = route.query.audio
  if (queryAudio === '0' || queryAudio === 'mute' || queryAudio === 'off') {
    audioSynth.isMuted.value = true
  } else if (queryAudio === '1' || queryAudio === 'on' || queryAudio === 'audio') {
    audioSynth.isMuted.value = false
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
