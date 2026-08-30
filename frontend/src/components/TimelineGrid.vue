<template>
  <div
    class="h-full w-full bg-[#000033] flex flex-col overflow-hidden relative select-none font-mono"
    @mouseenter="isPaused = true"
    @mouseleave="isPaused = false"
  >
    <!-- Fixed Column Headers -->
    <div class="h-7 sm:h-8 bg-[#000066] border-b border-[#333366] grid grid-cols-12 text-[10px] sm:text-xs font-bold tracking-wider text-[#FFFF00] px-2 sm:px-3 items-center z-10 shadow shrink-0">
      <div class="col-span-4 uppercase border-r border-[#333366] pr-1 sm:pr-2 truncate">SOURCE / VENUE</div>
      <div class="col-span-3 uppercase border-r border-[#333366] px-1 sm:px-2 text-[#00FFFF] truncate">TODAY</div>
      <div class="col-span-3 uppercase border-r border-[#333366] px-1 sm:px-2 text-[#00FFFF] truncate">TONIGHT</div>
      <div class="col-span-2 uppercase pl-1 sm:pl-2 text-[#00FFFF] truncate">TOMORROW</div>
    </div>

    <!-- Scrolling Grid Area -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto overflow-x-hidden scrollbar-none relative"
    >
      <div ref="scrollContent" class="space-y-0.5 py-0.5">
        <!-- Render double list for seamless continuous infinite looping -->
        <div
          v-for="(venue, idx) in displayedVenues"
          :key="`${venue.id}-${idx}`"
          class="grid grid-cols-12 text-[11px] sm:text-xs px-2 sm:px-3 py-1.5 sm:py-2 border-b border-[#222255] items-center hover:bg-[#000066]/70 transition-colors"
          :class="idx % 2 === 0 ? 'bg-[#000033]' : 'bg-[#000044]'"
        >
          <!-- Venue Name & Channel Number -->
          <div class="col-span-4 font-bold text-[#E0E0E0] truncate border-r border-[#333366] pr-1 sm:pr-2 flex items-center space-x-1 sm:space-x-2">
            <span class="text-[#8888AA] text-[9px] sm:text-[10px] shrink-0">{{ String((idx % venues.length) + 1).padStart(2, '0') }}</span>
            <span class="truncate uppercase text-[#FFFFFF]">{{ venue.name }}</span>
          </div>

          <!-- Today Events (< 5 PM) -->
          <div class="col-span-3 truncate border-r border-[#333366] px-1 sm:px-2">
            <template v-if="getVenueSlotEvents(venue.id, 'today').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'today')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1 sm:space-x-1.5 group"
              >
                <!-- Category Color Pip -->
                <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" :class="getCategoryColor(evt.category)"></span>

                <!-- Ticket Commitment Badge / Toggle Button -->
                <button
                  type="button"
                  class="shrink-0 text-[8px] sm:text-[9px] px-1 py-0.2 rounded-xs font-black cursor-pointer transition-all border"
                  :class="evt.has_ticket === 1
                    ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                    : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <!-- Event Title -->
                <span
                  class="truncate font-semibold cursor-pointer hover:underline"
                  :class="{ 'text-[#00FF00] font-black': evt.has_ticket === 1 }"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.title }}
                </span>

                <!-- Event Time -->
                <span class="text-[#00FFFF] text-[9px] sm:text-[10px] shrink-0">{{ formatEventTime(evt.start_time) }}</span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic text-[10px] sm:text-[11px]">[ Box Office Open ]</span>
          </div>

          <!-- Tonight Events (>= 5 PM) -->
          <div class="col-span-3 truncate border-r border-[#333366] px-1 sm:px-2">
            <template v-if="getVenueSlotEvents(venue.id, 'tonight').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'tonight')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1 sm:space-x-1.5 group"
              >
                <!-- Category Color Pip -->
                <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" :class="getCategoryColor(evt.category)"></span>

                <!-- Ticket Commitment Badge / Toggle Button -->
                <button
                  type="button"
                  class="shrink-0 text-[8px] sm:text-[9px] px-1 py-0.2 rounded-xs font-black cursor-pointer transition-all border"
                  :class="evt.has_ticket === 1
                    ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                    : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <!-- Event Title -->
                <span
                  class="truncate font-semibold cursor-pointer hover:underline"
                  :class="{ 'text-[#00FF00] font-black': evt.has_ticket === 1 }"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.title }}
                </span>

                <!-- Event Time -->
                <span class="text-[#00FFFF] text-[9px] sm:text-[10px] shrink-0">{{ formatEventTime(evt.start_time) }}</span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic text-[10px] sm:text-[11px]">[ Closed Tonight ]</span>
          </div>

          <!-- Tomorrow Events -->
          <div class="col-span-2 truncate pl-1 sm:pl-2">
            <template v-if="getVenueSlotEvents(venue.id, 'tomorrow').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'tomorrow')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1 sm:space-x-1.5 group"
              >
                <!-- Category Color Pip -->
                <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" :class="getCategoryColor(evt.category)"></span>

                <!-- Ticket Commitment Badge / Toggle Button -->
                <button
                  type="button"
                  class="shrink-0 text-[8px] sm:text-[9px] px-1 py-0.2 rounded-xs font-black cursor-pointer transition-all border"
                  :class="evt.has_ticket === 1
                    ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                    : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <!-- Event Title -->
                <span
                  class="truncate font-semibold cursor-pointer hover:underline"
                  :class="{ 'text-[#00FF00] font-black': evt.has_ticket === 1 }"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.title }}
                </span>

                <!-- Event Time -->
                <span class="text-[#00FFFF] text-[9px] sm:text-[10px] shrink-0">{{ formatEventTime(evt.start_time) }}</span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic text-[10px] sm:text-[11px]">[ No Listings ]</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { updateEvent } from '../api/client'
import type { EventItem, VenueItem } from '../types'

const props = withDefaults(
  defineProps<{
    venues: VenueItem[]
    events: EventItem[]
    scrollSpeed?: number
  }>(),
  {
    scrollSpeed: 60,
  }
)

const emit = defineEmits<{
  (e: 'ticket-toggled', eventId: string, hasTicket: number): void
}>()

const scrollContainer = ref<HTMLElement | null>(null)
const scrollContent = ref<HTMLElement | null>(null)
const isPaused = ref(false)
let animationFrameId: number | null = null

// Duplicate venue list to enable smooth infinite loop
const displayedVenues = computed(() => {
  if (props.venues.length === 0) return []
  return [...props.venues, ...props.venues]
})

function getCategoryColor(category: string): string {
  switch (category.toLowerCase()) {
    case 'music':
      return 'bg-[#00FFFF]' // Cyan
    case 'sports':
      return 'bg-[#FFFF00]' // Yellow
    case 'theater':
      return 'bg-[#FF00FF]' // Magenta
    case 'comedy':
      return 'bg-[#00FF00]' // Green
    case 'community':
      return 'bg-[#FFFFFF]' // White
    default:
      return 'bg-[#8888AA]'
  }
}

function formatEventTime(isoString: string): string {
  try {
    const d = new Date(isoString)
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  } catch {
    return ''
  }
}

function getVenueSlotEvents(venueId: string, slot: 'today' | 'tonight' | 'tomorrow'): EventItem[] {
  const now = new Date()
  const todayDateStr = now.toISOString().split('T')[0]

  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowDateStr = tomorrow.toISOString().split('T')[0]

  return props.events.filter(e => {
    if (e.venue_id !== venueId) return false
    const eventDate = new Date(e.start_time)
    const eventDateStr = e.start_time.split('T')[0]
    const eventHour = eventDate.getHours()

    if (slot === 'today') {
      return eventDateStr === todayDateStr && eventHour < 17
    } else if (slot === 'tonight') {
      return eventDateStr === todayDateStr && eventHour >= 17
    } else if (slot === 'tomorrow') {
      return eventDateStr === tomorrowDateStr
    }
    return false
  })
}

async function toggleTicketStatus(evt: EventItem) {
  const newStatus = evt.has_ticket === 1 ? 0 : 1
  evt.has_ticket = newStatus
  emit('ticket-toggled', evt.id, newStatus)
  try {
    await updateEvent(evt.id, { has_ticket: newStatus })
  } catch (err) {
    console.error('Failed to update event ticket commitment status:', err)
    evt.has_ticket = newStatus === 1 ? 0 : 1
  }
}

function startAutoScroll() {
  let lastTimestamp = performance.now()

  function step(currentTimestamp: number) {
    const deltaSeconds = (currentTimestamp - lastTimestamp) / 1000
    lastTimestamp = currentTimestamp

    if (!isPaused.value && scrollContainer.value && scrollContent.value) {
      const pixelsToMove = (props.scrollSpeed || 60) * deltaSeconds
      scrollContainer.value.scrollTop += pixelsToMove

      const halfHeight = scrollContent.value.scrollHeight / 2
      if (scrollContainer.value.scrollTop >= halfHeight) {
        scrollContainer.value.scrollTop -= halfHeight
      }
    }

    animationFrameId = requestAnimationFrame(step)
  }

  animationFrameId = requestAnimationFrame(step)
}

onMounted(() => {
  startAutoScroll()
})

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})
</script>
