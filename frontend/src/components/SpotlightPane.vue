<template>
  <div class="w-full h-full bg-[#000044] border-b-2 border-[#FFFF00] flex flex-col justify-between overflow-hidden select-none font-mono relative">
    <!-- TOP 2-COLUMN SPLIT PREVIEW BODY (CLASSIC 1990S PREVUE CABLE LAYOUT) -->
    <div class="flex-1 w-full flex flex-row items-stretch min-h-0 overflow-hidden px-2 pt-1.5 gap-3">
      <!-- LEFT COLUMN (48% on desktop / 45% mobile): FEATURED EVENT ARTWORK / CRT GRAPHICS / SPORTS MATCHUP VS CARD -->
      <div class="w-[48%] h-full flex flex-col justify-between border-2 border-[#00FFFF] bg-[#000022] overflow-hidden relative shadow-inner">
        <!-- Live Sports Matchup Graphic Card (When Category is Sports and teams are parsed) -->
        <div
          v-if="isSportsCategory && matchupTeams"
          class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000044] via-[#000022] to-[#000011] overflow-hidden"
        >
          <!-- Matchup Header -->
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <span class="text-[#FFFF00] font-black uppercase tracking-wider">
              [ {{ matchupTeams.league ? matchupTeams.league + ' LIVE MATCHUP' : 'LIVE MATCHUP' }} ]
            </span>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'MAIN ARENA' }}
            </span>
          </div>

          <!-- Extra Large Team VS Badges & Official Franchise Colors (Maximized Real Estate) -->
          <div class="flex items-center justify-around py-1 text-center my-auto w-full px-1">
            <!-- Home Team Card -->
            <div class="flex flex-col items-center space-y-1.5 sm:space-y-2 w-[44%]">
              <div
                class="w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 lg:w-36 lg:h-36 xl:w-40 xl:h-40 rounded-full border-3 sm:border-4 p-2 sm:p-3 flex items-center justify-center font-black relative overflow-hidden shadow-2xl transition-transform hover:scale-105"
                :style="{
                  borderColor: teamABranding?.secondaryColor || '#FFFF00',
                  backgroundColor: teamABranding?.primaryColor || '#000044',
                  boxShadow: `0 0 20px ${teamABranding?.secondaryColor || 'rgba(255,255,0,0.6)'}`
                }"
              >
                <!-- Large Logo Image with High-Res Acronym Fallback -->
                <img
                  v-if="teamABranding?.logoUrl && !teamALogoError"
                  :src="teamABranding.logoUrl"
                  :alt="teamABranding.name"
                  class="w-full h-full object-contain drop-shadow-lg"
                  @error="teamALogoError = true"
                />
                <span
                  v-else
                  class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl tracking-wider"
                  :style="{ color: teamABranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamABranding?.shortName || matchupTeams.teamA.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm md:text-base lg:text-lg font-black text-[#FFFFFF] truncate w-full leading-tight uppercase drop-shadow">
                {{ teamABranding?.name || matchupTeams.teamA }}
              </span>
            </div>

            <!-- Prominent Broadcast VS Lightning Graphic -->
            <div class="flex flex-col items-center shrink-0 px-2 sm:px-3">
              <span class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl text-[#FF4444] animate-pulse drop-shadow-[0_0_14px_rgba(255,68,68,0.95)]">
                VS
              </span>
              <span class="text-[10px] sm:text-xs text-[#00FFFF] font-black tracking-widest uppercase mt-0.5">MATCHUP</span>
            </div>

            <!-- Away Team Card -->
            <div class="flex flex-col items-center space-y-1.5 sm:space-y-2 w-[44%]">
              <div
                class="w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 lg:w-36 lg:h-36 xl:w-40 xl:h-40 rounded-full border-3 sm:border-4 p-2 sm:p-3 flex items-center justify-center font-black relative overflow-hidden shadow-2xl transition-transform hover:scale-105"
                :style="{
                  borderColor: teamBBranding?.secondaryColor || '#00FFFF',
                  backgroundColor: teamBBranding?.primaryColor || '#000044',
                  boxShadow: `0 0 20px ${teamBBranding?.secondaryColor || 'rgba(0,255,255,0.6)'}`
                }"
              >
                <!-- Large Logo Image with High-Res Acronym Fallback -->
                <img
                  v-if="teamBBranding?.logoUrl && !teamBLogoError"
                  :src="teamBBranding.logoUrl"
                  :alt="teamBBranding.name"
                  class="w-full h-full object-contain drop-shadow-lg"
                  @error="teamBLogoError = true"
                />
                <span
                  v-else
                  class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl tracking-wider"
                  :style="{ color: teamBBranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamBBranding?.shortName || matchupTeams.teamB.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm md:text-base lg:text-lg font-black text-[#FFFFFF] truncate w-full leading-tight uppercase drop-shadow">
                {{ teamBBranding?.name || matchupTeams.teamB }}
              </span>
            </div>
          </div>

          <!-- Matchup Footer Ribbon -->
          <div class="bg-[#000066] border border-[#00FFFF] px-2 py-0.5 sm:py-1 text-center text-xs sm:text-sm text-[#00FFFF] font-black uppercase truncate shrink-0">
            HEAD TO HEAD BROADCAST
          </div>
        </div>

        <!-- Featured Event Artwork Image with CRT Gradient Overlay -->
        <div v-else-if="currentEvent?.image_url" class="w-full h-full relative overflow-hidden flex items-center justify-center bg-black">
          <img
            :src="currentEvent.image_url"
            :alt="currentEvent.title"
            class="w-full h-full object-cover opacity-90 transition-transform duration-700 hover:scale-105"
            @error="handleImageError"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-[#000044] via-transparent to-black/40 pointer-events-none"></div>
          <div class="absolute top-2 left-2 bg-[#0000AA]/90 border border-[#FFFF00] px-2.5 py-0.5 text-xs sm:text-sm font-black text-[#FFFF00] uppercase tracking-wider shadow">
            HEADLINE PREVIEW
          </div>
        </div>

        <!-- Fallback Retro CRT Graphics Banner (Zero External Image) -->
        <div v-else class="w-full h-full flex flex-col justify-between p-3.5 bg-gradient-to-br from-[#000088] via-[#000044] to-[#000011]">
          <div class="flex items-center justify-between border-b border-[#FFFF00] pb-1">
            <span class="text-[#FFFF00] font-black text-xs sm:text-sm tracking-widest uppercase">PREVUE GUIDE</span>
            <span class="text-[#00FFFF] text-xs sm:text-sm font-bold">CH 03</span>
          </div>

          <div class="text-center my-auto space-y-1.5">
            <div class="text-base sm:text-lg font-black text-[#00FF00] tracking-wider uppercase drop-shadow">
              [ {{ currentEvent?.category || 'COMMUNITY' }} ]
            </div>
            <div class="text-sm sm:text-base md:text-lg text-[#E0E0E0] font-black uppercase line-clamp-2 px-1">
              {{ currentEvent?.title || 'TONIGHT ON PREVUE' }}
            </div>
          </div>

          <div class="bg-[#000022] border border-[#333366] px-2 py-1 text-center text-xs text-[#8888AA] font-bold uppercase">
            UPCOMING EVENT SPOTLIGHT
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN (52%): RETRO CABLE BULLETIN TEXT, DETAILS & TICKET PASS -->
      <div class="w-[52%] h-full flex flex-col justify-between py-1 pr-1 font-mono min-h-0 overflow-hidden">
        <div class="space-y-1.5 overflow-hidden">
          <!-- Top Meta Tag -->
          <div class="flex items-center justify-between text-xs sm:text-sm border-b border-[#333366] pb-1 shrink-0">
            <div class="flex items-center space-x-2 truncate">
              <span class="text-[#00FFFF] font-black tracking-wider uppercase truncate text-xs sm:text-sm">
                [ {{ currentEvent?.category || 'FEATURED' }} ]
              </span>
              <span
                v-if="currentEvent?.has_ticket === 1"
                class="bg-[#00FF00] text-[#000033] text-xs px-2 py-0.5 font-black rounded-xs shadow-[0_0_6px_rgba(0,255,0,0.8)] shrink-0"
              >
                [TICKET OWNED]
              </span>
            </div>
            <span class="text-[#8888AA] text-xs sm:text-sm shrink-0 font-black">
              SPOTLIGHT {{ currentIndex + 1 }} OF {{ featuredEvents.length }}
            </span>
          </div>

          <!-- Venue Name -->
          <div class="text-xs sm:text-sm md:text-base text-[#E0E0E0] uppercase tracking-wide truncate shrink-0 font-bold">
            VENUE: <span class="text-[#FFFFFF] font-black">{{ currentEvent?.venue_name || 'MAIN STAGE' }}</span>
          </div>

          <!-- Event Title (Large Chunky 1990s TV Typography) -->
          <div class="text-base sm:text-lg md:text-xl lg:text-2xl font-black text-[#FFFF00] leading-tight line-clamp-2 tracking-wide drop-shadow-md uppercase shrink-0">
            {{ currentEvent?.title || 'NO FEATURED EVENTS SCHEDULED' }}
          </div>

          <!-- Date & Time -->
          <div class="text-xs sm:text-sm md:text-base text-[#00FFFF] font-bold truncate shrink-0">
            DATE: <span class="text-[#00FF00] font-black">{{ formattedDate }}</span>
          </div>

          <!-- Price Range -->
          <div class="text-xs sm:text-sm md:text-base text-[#00FF00] font-bold truncate shrink-0">
            TICKETS: <span class="text-[#FFFF00] font-black">{{ formattedPrice }}</span>
          </div>

          <!-- Description Snippet -->
          <p v-if="currentEvent?.description" class="text-xs sm:text-sm text-[#A0A0C0] line-clamp-2 leading-relaxed pt-0.5 hidden sm:block overflow-hidden font-medium">
            {{ currentEvent.description }}
          </p>
        </div>

        <!-- Bottom: High-Contrast Scannable Box Office Mobile QR Pass & Rotation Dots -->
        <div class="flex items-center justify-between pt-1.5 border-t border-[#333366] shrink-0">
          <div class="flex items-center space-x-2 sm:space-x-3">
            <!-- Large High-Contrast Scannable QR Code Pass (Engineered for Scanline Resistance) -->
            <div
              v-if="qrCodeDataUrl"
              class="bg-white p-1 rounded-xs border-2 border-[#FFFF00] shadow-[0_0_10px_rgba(255,255,0,0.7)] shrink-0 cursor-pointer transition-transform hover:scale-110"
              @click="isQrModalOpen = true"
              title="Click to expand high-resolution ticket QR pass"
            >
              <img
                :src="qrCodeDataUrl"
                alt="Ticket QR Pass"
                class="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 object-contain"
              />
            </div>
            <div class="text-xs text-[#8888AA] leading-tight hidden sm:block">
              <span class="text-[#FFFF00] font-black block tracking-wider text-xs">BOX OFFICE PASS</span>
              <span class="text-[#00FF00] font-black text-xs">HIGH-RES SCAN</span>
            </div>
          </div>

          <!-- Rotation Indicator Dots -->
          <div class="flex space-x-1.5 sm:space-x-2">
            <button
              v-for="(_, idx) in featuredEvents.slice(0, 8)"
              :key="idx"
              type="button"
              class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full transition-all cursor-pointer"
              :class="idx === currentIndex ? 'bg-[#FFFF00] scale-125 shadow-[0_0_6px_rgba(255,255,0,0.8)]' : 'bg-[#333366] hover:bg-[#8888AA]'"
              @click="setIndex(idx)"
            ></button>
          </div>
        </div>
      </div>
    </div>

    <!-- OVERLAYED TRANSLUCENT SPOTIFY MARQUEE TICKER (IN-FLOW BOTTOM EDGE) -->
    <div class="h-7 sm:h-8 w-full bg-[#000022]/90 backdrop-blur-xs border-t border-[#1DB954]/50 flex items-center justify-between px-3 text-xs sm:text-sm font-mono text-[#E0E0E0] shrink-0 select-none shadow-md z-10">
      <!-- Left: Equalizer Graphic & Spotify Branding -->
      <div class="flex items-center space-x-2 shrink-0">
        <button
          type="button"
          class="flex items-center space-x-1.5 cursor-pointer hover:opacity-80 transition-opacity"
          @click="openSpotifyModal"
          title="Open Spotify Audio Player"
        >
          <div class="flex items-end space-x-0.5 h-3.5 text-[#1DB954]">
            <span class="w-0.5 bg-current animate-pulse h-2"></span>
            <span class="w-0.5 bg-current animate-pulse h-3.5"></span>
            <span class="w-0.5 bg-current animate-pulse h-2"></span>
          </div>
          <span class="font-black text-xs sm:text-sm tracking-wider text-[#1DB954]">
            SPOTIFY HEADEND
          </span>
        </button>
      </div>

      <!-- Center: Marquee Scrolling Stream Track (Pulled Dynamically from Spotify) -->
      <div class="flex-1 mx-3 overflow-hidden whitespace-nowrap text-center">
        <span class="text-[#FFFF00] font-black tracking-widest uppercase inline-block text-xs sm:text-sm">
          NOW PLAYING: "{{ dynamicSpotifyTitle }}" {{ dynamicSpotifyAuthor ? 'BY ' + dynamicSpotifyAuthor.toUpperCase() : '' }} [12 kHz RF FILTER ACTIVE]
        </span>
      </div>

      <!-- Right: Direct Play / Launch Action Button -->
      <div class="flex items-center space-x-1.5 shrink-0">
        <button
          type="button"
          class="bg-[#1DB954] text-[#000033] hover:bg-white px-2.5 py-0.5 font-black text-xs tracking-wider transition-all cursor-pointer shadow-[0_0_6px_rgba(29,185,84,0.6)]"
          @click="openSpotifyModal"
          title="Start or action Spotify music playback"
        >
          [ PLAY SPOTIFY ]
        </button>
      </div>
    </div>

    <!-- FULL-SCREEN QR CODE EXPANDED DIALOG (HIGH SCAN RESISTANCE MODAL) -->
    <div
      v-if="isQrModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xs p-4 select-none"
      @click.self="isQrModalOpen = false"
    >
      <div class="bg-gradient-to-b from-[#000088] via-[#000044] to-[#000022] border-2 border-[#FFFF00] rounded-xs shadow-[0_0_30px_rgba(255,255,0,0.8)] p-6 max-w-sm w-full text-center space-y-4 font-mono">
        <div class="flex items-center justify-between border-b border-[#FFFF00] pb-2">
          <span class="text-sm font-black text-[#FFFF00] uppercase tracking-wider">[ BOX OFFICE MOBILE PASS ]</span>
          <button
            type="button"
            class="text-xs text-[#00FFFF] hover:text-white font-bold cursor-pointer"
            @click="isQrModalOpen = false"
          >
            [ X CLOSE ]
          </button>
        </div>

        <div class="bg-white p-3 rounded-xs border-4 border-[#00FFFF] inline-block shadow-2xl">
          <img :src="qrCodeDataUrl || ''" alt="Enlarged QR Code" class="w-52 h-52 sm:w-60 sm:h-60 object-contain" />
        </div>

        <div class="space-y-1">
          <div class="text-sm font-black text-[#FFFF00] uppercase">{{ currentEvent?.title }}</div>
          <div class="text-xs text-[#00FF00] font-bold">{{ currentEvent?.venue_name }}</div>
          <div class="text-xs text-[#8888AA]">Scan directly with your phone camera to open tickets.</div>
        </div>

        <div class="pt-2 border-t border-[#333366]">
          <a
            :href="currentEvent?.ticket_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block bg-[#FFFF00] text-[#000033] hover:bg-white px-4 py-2 text-xs sm:text-sm font-black tracking-wider transition-all"
          >
            [ OPEN TICKET LINK DIRECTLY ]
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { fetchSpotifyMetadata } from '../api/client'
import { parseMatchup, resolveTeamBranding } from '../services/sportsTheme'
import { openSpotifyModal } from '../services/spotifyModalState'
import type { EventItem } from '../types'

const props = withDefaults(
  defineProps<{
    events: EventItem[]
    rotationSeconds?: number
  }>(),
  {
    events: () => [],
    rotationSeconds: 20,
  }
)

const currentIndex = ref(0)
const qrCodeDataUrl = ref<string | null>(null)
const isQrModalOpen = ref(false)
const teamALogoError = ref(false)
const teamBLogoError = ref(false)
let rotationTimer: ReturnType<typeof setInterval> | null = null

// Dynamically resolved Spotify playlist details from oEmbed API
const dynamicSpotifyTitle = ref('OPENPREVUE')
const dynamicSpotifyAuthor = ref('UPIONEER')

async function loadSpotifyMeta() {
  try {
    const meta = await fetchSpotifyMetadata()
    if (meta.title) {
      dynamicSpotifyTitle.value = meta.title.toUpperCase()
    }
    if (meta.author_name) {
      dynamicSpotifyAuthor.value = meta.author_name.toUpperCase()
    }
  } catch {
    // Keep defaults
  }
}

// Fallback image error flag per event
const imageErrorMap = ref<Record<string, boolean>>({})

function handleImageError(e: Event) {
  const target = e.target as HTMLImageElement
  if (currentEvent.value) {
    imageErrorMap.value[currentEvent.value.id] = true
  }
  target.style.display = 'none'
}

// Filter featured events, or fallback to all events if none flagged featured
const featuredEvents = computed(() => {
  if (!props.events || props.events.length === 0) return []
  const explicitFeatured = props.events.filter(e => e.is_featured === 1)
  return explicitFeatured.length > 0 ? explicitFeatured : props.events.slice(0, 10)
})

const currentEvent = computed<EventItem | null>(() => {
  if (featuredEvents.value.length === 0) return null
  return featuredEvents.value[currentIndex.value % featuredEvents.value.length]
})

const isSportsCategory = computed(() => {
  return currentEvent.value?.category?.toLowerCase() === 'sports'
})

// Parse Sports matchup teams using robust case-insensitive parser
const matchupTeams = computed(() => {
  if (!currentEvent.value || !isSportsCategory.value) return null
  return parseMatchup(currentEvent.value.title)
})

const teamABranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamA)
})

const teamBBranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamB)
})

const formattedDate = computed(() => {
  if (!currentEvent.value?.start_time) return 'TBA'
  try {
    const d = new Date(currentEvent.value.start_time)
    return d.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).toUpperCase()
  } catch {
    return currentEvent.value.start_time
  }
})

const formattedPrice = computed(() => {
  if (!currentEvent.value) return 'FREE'
  if (currentEvent.value.price_min === undefined || currentEvent.value.price_min === null) {
    return 'CHECK BOX OFFICE'
  }
  if (currentEvent.value.price_min === 0 && (!currentEvent.value.price_max || currentEvent.value.price_max === 0)) {
    return 'FREE ADMISSION'
  }
  const curr = currentEvent.value.currency || '$'
  if (currentEvent.value.price_max && currentEvent.value.price_max > currentEvent.value.price_min) {
    return `${curr}${currentEvent.value.price_min.toFixed(0)} - ${curr}${currentEvent.value.price_max.toFixed(0)}`
  }
  return `${curr}${currentEvent.value.price_min.toFixed(0)}`
})

async function generateQrCode() {
  if (!currentEvent.value?.ticket_url) {
    qrCodeDataUrl.value = null
    return
  }
  try {
    // Generate high resolution QR code with High (30%) Error Correction Level
    qrCodeDataUrl.value = await QRCode.toDataURL(currentEvent.value.ticket_url, {
      margin: 1,
      width: 256,
      errorCorrectionLevel: 'H',
      color: {
        dark: '#000000',
        light: '#FFFFFF',
      },
    })
  } catch {
    qrCodeDataUrl.value = null
  }
}

function setIndex(index: number) {
  currentIndex.value = index
  teamALogoError.value = false
  teamBLogoError.value = false
  generateQrCode()
  restartRotationTimer()
}

function nextSlide() {
  if (featuredEvents.value.length === 0) return
  currentIndex.value = (currentIndex.value + 1) % featuredEvents.value.length
  teamALogoError.value = false
  teamBLogoError.value = false
  generateQrCode()
}

function restartRotationTimer() {
  if (rotationTimer) clearInterval(rotationTimer)
  const seconds = props.rotationSeconds || 20
  rotationTimer = setInterval(nextSlide, seconds * 1000)
}

watch(
  () => props.rotationSeconds,
  () => {
    restartRotationTimer()
  }
)

watch(
  () => props.events,
  () => {
    if (currentIndex.value >= featuredEvents.value.length) {
      currentIndex.value = 0
    }
    teamALogoError.value = false
    teamBLogoError.value = false
    generateQrCode()
  },
  { deep: true }
)

watch(
  () => currentEvent.value,
  () => {
    teamALogoError.value = false
    teamBLogoError.value = false
    generateQrCode()
  }
)

onMounted(() => {
  generateQrCode()
  restartRotationTimer()
  loadSpotifyMeta()
})

onUnmounted(() => {
  if (rotationTimer) clearInterval(rotationTimer)
})
</script>
