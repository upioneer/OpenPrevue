<template>
  <div
    class="h-full w-full bg-[#000033] flex flex-col overflow-hidden relative select-none font-mono"
    @mouseenter="isHoverPaused = true"
    @mouseleave="isHoverPaused = false"
  >
    <!-- Fixed Column Headers -->
    <div
      class="bg-[#000066] border-b-2 border-[#333366] grid grid-cols-12 font-black tracking-wider text-[#FFFF00] px-3 sm:px-4 items-center z-10 shadow shrink-0"
      :class="headerClasses"
    >
      <div class="col-span-4 uppercase border-r-2 border-[#333366] pr-2 truncate">SOURCE / VENUE</div>
      <div class="col-span-3 uppercase border-r-2 border-[#333366] px-2 text-[#00FFFF] truncate">TODAY</div>
      <div class="col-span-3 uppercase border-r-2 border-[#333366] px-2 text-[#00FFFF] truncate">TONIGHT</div>
      <div class="col-span-2 uppercase pl-2 text-[#00FFFF] truncate">TOMORROW</div>
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
          class="grid grid-cols-12 px-3 sm:px-4 border-b border-[#222255] items-center hover:bg-[#000066]/70 transition-colors"
          :class="[
            idx % 2 === 0 ? 'bg-[#000033]' : 'bg-[#000044]',
            rowDensityClasses
          ]"
        >
          <!-- Venue Name & Channel Number -->
          <div class="col-span-4 font-black text-[#E0E0E0] truncate border-r-2 border-[#333366] pr-2 flex items-center space-x-1.5 sm:space-x-2.5">
            <span class="text-[#8888AA] shrink-0 font-bold" :class="channelNumClasses">
              {{ String((idx % venues.length) + 1).padStart(2, '0') }}
            </span>
            <span class="truncate uppercase text-[#FFFFFF] font-black" :class="venueTitleClasses">
              {{ venue.name }}
            </span>
          </div>

          <!-- Today Events (< 5 PM) -->
          <div class="col-span-3 truncate border-r-2 border-[#333366] px-2">
            <template v-if="getVenueSlotEvents(venue.id, 'today').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'today')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1.5 sm:space-x-2 group"
              >
                <!-- Category Color Pip -->
                <span
                  class="rounded-full inline-block shrink-0 shadow-[0_0_4px_currentColor]"
                  :class="[getCategoryColor(evt.category), pipSizeClasses]"
                ></span>

                <!-- Sports League & Team Badges if Sports Matchup -->
                <template v-if="getSportsDetails(evt)">
                  <span
                    v-if="getSportsDetails(evt)?.league"
                    class="bg-[#000088] text-[#00FFFF] border border-[#00FFFF] font-black rounded-xs shrink-0 uppercase"
                    :class="leagueBadgeClasses"
                  >
                    {{ getSportsDetails(evt)?.league }}
                  </span>
                  <div class="flex items-center space-x-1 shrink-0">
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamA.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamA.secondaryColor,
                        color: getSportsDetails(evt)?.teamA.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamA.shortName }}
                    </span>
                    <span class="font-black text-[#FF4444]" :class="vsTextClasses">VS</span>
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamB.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamB.secondaryColor,
                        color: getSportsDetails(evt)?.teamB.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamB.shortName }}
                    </span>
                  </div>
                </template>

                <!-- Ticket Commitment Badge / Toggle Button -->
                <button
                  type="button"
                  class="shrink-0 rounded-xs font-black cursor-pointer transition-all border"
                  :class="[
                    ticketButtonClasses,
                    evt.has_ticket === 1
                      ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                      : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'
                  ]"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <!-- Event Title -->
                <span
                  class="truncate font-bold cursor-pointer hover:underline"
                  :class="[
                    eventTitleClasses,
                    evt.has_ticket === 1 ? 'text-[#00FF00] font-black' : ''
                  ]"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ formatDisplayTitle(evt) }}
                </span>

                <!-- Event Time -->
                <span class="text-[#00FFFF] shrink-0 font-bold" :class="eventTimeClasses">
                  {{ formatEventTime(evt.start_time) }}
                </span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic" :class="emptySlotClasses">[ Box Office Open ]</span>
          </div>

          <!-- Tonight Events (>= 5 PM) -->
          <div class="col-span-3 truncate border-r-2 border-[#333366] px-2">
            <template v-if="getVenueSlotEvents(venue.id, 'tonight').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'tonight')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1.5 sm:space-x-2 group"
              >
                <span
                  class="rounded-full inline-block shrink-0 shadow-[0_0_4px_currentColor]"
                  :class="[getCategoryColor(evt.category), pipSizeClasses]"
                ></span>

                <!-- Sports League & Team Badges if Sports Matchup -->
                <template v-if="getSportsDetails(evt)">
                  <span
                    v-if="getSportsDetails(evt)?.league"
                    class="bg-[#000088] text-[#00FFFF] border border-[#00FFFF] font-black rounded-xs shrink-0 uppercase"
                    :class="leagueBadgeClasses"
                  >
                    {{ getSportsDetails(evt)?.league }}
                  </span>
                  <div class="flex items-center space-x-1 shrink-0">
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamA.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamA.secondaryColor,
                        color: getSportsDetails(evt)?.teamA.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamA.shortName }}
                    </span>
                    <span class="font-black text-[#FF4444]" :class="vsTextClasses">VS</span>
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamB.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamB.secondaryColor,
                        color: getSportsDetails(evt)?.teamB.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamB.shortName }}
                    </span>
                  </div>
                </template>

                <button
                  type="button"
                  class="shrink-0 rounded-xs font-black cursor-pointer transition-all border"
                  :class="[
                    ticketButtonClasses,
                    evt.has_ticket === 1
                      ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                      : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'
                  ]"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <span
                  class="truncate font-bold cursor-pointer hover:underline"
                  :class="[
                    eventTitleClasses,
                    evt.has_ticket === 1 ? 'text-[#00FF00] font-black' : ''
                  ]"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ formatDisplayTitle(evt) }}
                </span>

                <span class="text-[#00FFFF] shrink-0 font-bold" :class="eventTimeClasses">
                  {{ formatEventTime(evt.start_time) }}
                </span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic" :class="emptySlotClasses">[ Box Office Open ]</span>
          </div>

          <!-- Tomorrow Events -->
          <div class="col-span-2 truncate pl-2">
            <template v-if="getVenueSlotEvents(venue.id, 'tomorrow').length > 0">
              <div
                v-for="evt in getVenueSlotEvents(venue.id, 'tomorrow')"
                :key="evt.id"
                class="truncate text-[#FFFF00] flex items-center space-x-1.5 sm:space-x-2 group"
              >
                <span
                  class="rounded-full inline-block shrink-0 shadow-[0_0_4px_currentColor]"
                  :class="[getCategoryColor(evt.category), pipSizeClasses]"
                ></span>

                <!-- Sports League & Team Badges if Sports Matchup -->
                <template v-if="getSportsDetails(evt)">
                  <span
                    v-if="getSportsDetails(evt)?.league"
                    class="bg-[#000088] text-[#00FFFF] border border-[#00FFFF] font-black rounded-xs shrink-0 uppercase"
                    :class="leagueBadgeClasses"
                  >
                    {{ getSportsDetails(evt)?.league }}
                  </span>
                  <div class="flex items-center space-x-1 shrink-0">
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamA.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamA.secondaryColor,
                        color: getSportsDetails(evt)?.teamA.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamA.shortName }}
                    </span>
                    <span class="font-black text-[#FF4444]" :class="vsTextClasses">VS</span>
                    <span
                      class="font-black rounded-xs border shrink-0"
                      :class="teamPillClasses"
                      :style="{
                        backgroundColor: getSportsDetails(evt)?.teamB.primaryColor,
                        borderColor: getSportsDetails(evt)?.teamB.secondaryColor,
                        color: getSportsDetails(evt)?.teamB.textColor
                      }"
                    >
                      {{ getSportsDetails(evt)?.teamB.shortName }}
                    </span>
                  </div>
                </template>

                <button
                  type="button"
                  class="shrink-0 rounded-xs font-black cursor-pointer transition-all border"
                  :class="[
                    ticketButtonClasses,
                    evt.has_ticket === 1
                      ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_6px_rgba(0,255,0,0.8)]'
                      : 'bg-transparent text-[#555577] border-[#333355] opacity-0 group-hover:opacity-100 hover:text-[#00FFFF] hover:border-[#00FFFF]'
                  ]"
                  :title="evt.has_ticket === 1 ? 'Committed: Ticket Owned (Click to toggle)' : 'Click to mark as Committed Ticket'"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ evt.has_ticket === 1 ? '[TICKET]' : '[+TKT]' }}
                </button>

                <span
                  class="truncate font-bold cursor-pointer hover:underline"
                  :class="[
                    eventTitleClasses,
                    evt.has_ticket === 1 ? 'text-[#00FF00] font-black' : ''
                  ]"
                  @click.stop="toggleTicketStatus(evt)"
                >
                  {{ formatDisplayTitle(evt) }}
                </span>

                <span class="text-[#00FFFF] shrink-0 font-bold" :class="eventTimeClasses">
                  {{ formatEventTime(evt.start_time) }}
                </span>
              </div>
            </template>
            <span v-else class="text-[#555577] italic" :class="emptySlotClasses">[ No Listings ]</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { updateEvent } from '../api/client'
import { parseMatchup, resolveTeamBranding, type TeamBranding } from '../services/sportsTheme'
import type { EventItem, VenueItem } from '../types'

const props = withDefaults(
  defineProps<{
    venues: VenueItem[]
    events: EventItem[]
    scrollSpeed?: number
    gridDensity?: 'classic_tv' | 'balanced' | 'dense' | string
    pauseDurationSeconds?: number
    pageIntervalSeconds?: number
  }>(),
  {
    scrollSpeed: 30,
    gridDensity: 'classic_tv',
    pauseDurationSeconds: 4,
    pageIntervalSeconds: 6,
  }
)

const emit = defineEmits<{
  (e: 'ticket-toggled', eventId: string, hasTicket: number): void
}>()

const scrollContainer = ref<HTMLElement | null>(null)
const scrollContent = ref<HTMLElement | null>(null)
const isHoverPaused = ref(false)
let animationFrameId: number | null = null

// Authentic 1990s Content-Quantized Row Snapping State Machine
let scrollPhase: 'scrolling' | 'pausing' = 'pausing'
let phaseTimer = 0
let currentTargetTop = 0
let targetRowIndex = 0

// Density Computed Classes for 4 Rows (Classic TV), 7 Rows (Balanced), 12 Rows (Dense)
const headerClasses = computed(() => {
  if (props.gridDensity === 'dense') {
    return 'h-7 sm:h-8 text-[11px] sm:text-xs'
  } else if (props.gridDensity === 'balanced') {
    return 'h-8 sm:h-9 text-xs sm:text-sm'
  }
  // classic_tv (4 rows default)
  return 'h-9 sm:h-11 text-xs sm:text-sm md:text-base'
})

const rowDensityClasses = computed(() => {
  if (props.gridDensity === 'dense') {
    return 'py-1 sm:py-1.5 min-h-[34px] sm:min-h-[38px]'
  } else if (props.gridDensity === 'balanced') {
    return 'py-2 sm:py-2.5 min-h-[46px] sm:min-h-[52px]'
  }
  // classic_tv (4 rows default) - Generous CRT broadcast row scale
  return 'py-3 sm:py-4 md:py-5 min-h-[64px] sm:min-h-[78px] md:min-h-[88px]'
})

const channelNumClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[9px] sm:text-[10px]'
  if (props.gridDensity === 'balanced') return 'text-[10px] sm:text-xs'
  return 'text-xs sm:text-sm md:text-base font-black'
})

const venueTitleClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[11px] sm:text-xs'
  if (props.gridDensity === 'balanced') return 'text-xs sm:text-sm md:text-base'
  return 'text-sm sm:text-base md:text-lg lg:text-xl'
})

const pipSizeClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'w-1.5 h-1.5'
  if (props.gridDensity === 'balanced') return 'w-2 h-2'
  return 'w-2.5 h-2.5 sm:w-3 sm:h-3'
})

const leagueBadgeClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[8px] px-1 py-0.1'
  if (props.gridDensity === 'balanced') return 'text-[9px] sm:text-[10px] px-1.5 py-0.2'
  return 'text-[10px] sm:text-xs md:text-sm px-2 py-0.5'
})

const teamPillClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[8px] px-1 py-0.1'
  if (props.gridDensity === 'balanced') return 'text-[9px] sm:text-[10px] px-1.5 py-0.2'
  return 'text-[10px] sm:text-xs md:text-sm px-2 py-0.5'
})

const vsTextClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[8px]'
  if (props.gridDensity === 'balanced') return 'text-[9px] sm:text-[10px]'
  return 'text-xs sm:text-sm font-black'
})

const ticketButtonClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[8px] px-1 py-0.1'
  if (props.gridDensity === 'balanced') return 'text-[9px] sm:text-[10px] px-1.5 py-0.2'
  return 'text-[10px] sm:text-xs px-2 py-0.5'
})

const eventTitleClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[11px] sm:text-xs'
  if (props.gridDensity === 'balanced') return 'text-xs sm:text-sm'
  return 'text-sm sm:text-base md:text-lg font-black'
})

const eventTimeClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[9px] sm:text-[10px]'
  if (props.gridDensity === 'balanced') return 'text-xs sm:text-sm'
  return 'text-xs sm:text-sm md:text-base'
})

const emptySlotClasses = computed(() => {
  if (props.gridDensity === 'dense') return 'text-[10px]'
  if (props.gridDensity === 'balanced') return 'text-xs'
  return 'text-xs sm:text-sm md:text-base'
})

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

function getSportsDetails(evt: EventItem): { league?: string; teamA: TeamBranding; teamB: TeamBranding } | null {
  if (evt.category.toLowerCase() !== 'sports') return null
  const parsed = parseMatchup(evt.title)
  if (!parsed) return null
  return {
    league: parsed.league,
    teamA: resolveTeamBranding(parsed.teamA),
    teamB: resolveTeamBranding(parsed.teamB),
  }
}

function formatDisplayTitle(evt: EventItem): string {
  const sports = getSportsDetails(evt)
  if (sports) {
    return `${sports.teamA.name} vs ${sports.teamB.name}`
  }
  return evt.title
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
    const deltaSeconds = Math.min((currentTimestamp - lastTimestamp) / 1000, 0.1)
    lastTimestamp = currentTimestamp

    if (!isHoverPaused.value && scrollContainer.value && scrollContent.value) {
      const container = scrollContainer.value
      const content = scrollContent.value
      const rows = content.children
      const pauseDuration = props.pauseDurationSeconds !== undefined ? props.pauseDurationSeconds : 4
      const halfHeight = content.scrollHeight / 2

      if (pauseDuration > 0 && rows.length > 0) {
        if (scrollPhase === 'pausing') {
          phaseTimer += deltaSeconds
          if (phaseTimer >= pauseDuration) {
            // Initiate next clean page advance
            phaseTimer = 0
            scrollPhase = 'scrolling'

            // Compute how many full rows fit neatly in visible container height
            const firstRowHeight = (rows[0] as HTMLElement)?.offsetHeight || 60
            const visibleRowCount = Math.max(1, Math.floor(container.clientHeight / firstRowHeight) - 1)
            targetRowIndex += visibleRowCount

            if (targetRowIndex < rows.length) {
              const targetEl = rows[targetRowIndex] as HTMLElement
              currentTargetTop = targetEl ? targetEl.offsetTop : container.scrollTop + (visibleRowCount * firstRowHeight)
            } else {
              currentTargetTop = container.scrollTop + (visibleRowCount * firstRowHeight)
            }
          }
        } else if (scrollPhase === 'scrolling') {
          const pixelsToMove = (props.scrollSpeed || 30) * deltaSeconds
          container.scrollTop += pixelsToMove

          // Snap cleanly to the exact row boundary when reached
          if (container.scrollTop >= currentTargetTop) {
            container.scrollTop = currentTargetTop
            scrollPhase = 'pausing'
            phaseTimer = 0

            // Seamless infinite wrap check on clean boundary
            if (halfHeight > 0 && container.scrollTop >= halfHeight) {
              container.scrollTop -= halfHeight
              currentTargetTop -= halfHeight
              targetRowIndex = 0
              for (let i = 0; i < rows.length; i++) {
                if ((rows[i] as HTMLElement).offsetTop >= container.scrollTop) {
                  targetRowIndex = i
                  break
                }
              }
            }
          }
        }
      } else {
        // Continuous non-stop scroll mode if pause duration is 0
        const pixelsToMove = (props.scrollSpeed || 30) * deltaSeconds
        container.scrollTop += pixelsToMove
        if (halfHeight > 0 && container.scrollTop >= halfHeight) {
          container.scrollTop -= halfHeight
        }
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
