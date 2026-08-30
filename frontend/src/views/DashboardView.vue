<template>
  <main class="flex-1 flex flex-col w-full h-full overflow-hidden relative">
    <!-- Top Pane: Spotlight Promo (45% Landscape / 34% Portrait) -->
    <div class="h-[45%] portrait-spotlight-height w-full shrink-0">
      <SpotlightPane
        :events="events"
        :rotation-seconds="marqueeRotationSeconds"
      />
    </div>

    <!-- Middle Ribbon: Divider Status Bar (6% Landscape / 5% Portrait) -->
    <div class="h-[6%] portrait-ribbon-height w-full shrink-0">
      <DividerRibbon
        :metro-label="settings?.metro_label || 'NEW ORLEANS'"
        :radius-miles="settings?.radius_miles || '35'"
      />
    </div>

    <!-- Bottom Pane: Scrolling Timeline Grid (49% Landscape / 61% Portrait) -->
    <div class="h-[49%] portrait-grid-height w-full flex-1 overflow-hidden">
      <TimelineGrid
        :venues="venues"
        :events="events"
        :scroll-speed="scrollSpeed"
        @ticket-toggled="handleTicketToggled"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import SpotlightPane from '../components/SpotlightPane.vue'
import DividerRibbon from '../components/DividerRibbon.vue'
import TimelineGrid from '../components/TimelineGrid.vue'
import { fetchEvents, fetchSettings, fetchVenues } from '../api/client'
import { wsService } from '../services/websocket'
import type { EventItem, SystemSettings, VenueItem } from '../types'

const events = ref<EventItem[]>([])
const venues = ref<VenueItem[]>([])
const settings = ref<SystemSettings | null>(null)
let refreshInterval: ReturnType<typeof setInterval> | null = null
let unsubscribeEventsWs: (() => void) | null = null
let unsubscribeSettingsWs: (() => void) | null = null

const marqueeRotationSeconds = computed(() => {
  if (!settings.value?.marquee_rotation_seconds) return 20
  return parseInt(settings.value.marquee_rotation_seconds, 10) || 20
})

const scrollSpeed = computed(() => {
  if (!settings.value?.autoscroll_speed) return 60
  return parseInt(settings.value.autoscroll_speed, 10) || 60
})

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
  } catch (err) {
    console.error('Failed to load dashboard data:', err)
  }
}

function handleTicketToggled(eventId: string, hasTicket: number) {
  const target = events.value.find(e => e.id === eventId)
  if (target) {
    target.has_ticket = hasTicket
  }
}

onMounted(() => {
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
  if (refreshInterval) clearInterval(refreshInterval)
  if (unsubscribeEventsWs) unsubscribeEventsWs()
  if (unsubscribeSettingsWs) unsubscribeSettingsWs()
})
</script>
