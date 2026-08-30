<template>
  <div class="h-full w-full bg-gradient-to-b from-[#000088] via-[#000044] to-[#000022] border-b-2 border-[#FFFF00] p-2.5 sm:p-3 flex flex-col justify-between overflow-hidden select-none relative">
    
    <!-- Top Content Area: Split 2-Column Promo & Text -->
    <div class="flex-1 w-full flex flex-row gap-2.5 sm:gap-4 overflow-hidden">
      <!-- Left: Event Promo Media Box / Sports Matchup Graphic / Commercial Video Player -->
      <div class="w-[38%] sm:w-[45%] h-full flex flex-col items-center justify-center bg-[#000022] border-2 border-[#333366] rounded-sm overflow-hidden relative shadow-inner shrink-0">
        
        <!-- Option 1: Live Video Commercial / Station Bumper Player -->
        <div v-if="commercialsEngine.isPlayingCommercial.value && commercialsEngine.currentClip.value" class="w-full h-full relative bg-black flex items-center justify-center">
          <video
            :src="commercialsEngine.currentClip.value.url"
            autoplay
            playsinline
            class="w-full h-full object-contain"
            @ended="commercialsEngine.onCommercialFinished"
          ></video>
          <div class="absolute top-1 left-1 bg-[#FFFF00] text-[#000033] px-1.5 py-0.2 text-[9px] font-black tracking-wider uppercase animate-pulse shadow">
            [ COMMERCIAL BREAK ]
          </div>
          <button
            type="button"
            class="absolute top-1 right-1 bg-[#000022]/80 text-[#8888AA] hover:text-[#FFFFFF] text-[9px] px-1 font-bold cursor-pointer"
            @click="commercialsEngine.onCommercialFinished"
            title="Skip Commercial"
          >
            [ SKIP ]
          </button>
        </div>

        <!-- Option 2: Authentic Sports Matchup Graphic with Vector Logos -->
        <div v-else-if="sportsMatchup && sportsMatchup.isMatchup" class="w-full h-full flex flex-col items-center justify-between p-1.5 sm:p-2 bg-gradient-to-b from-[#000055] via-[#000033] to-[#000011] relative overflow-hidden">
          <!-- Top League Banner -->
          <div class="w-full bg-[#000080] border-b border-[#FFFF00] py-0.5 text-center text-[10px] sm:text-xs font-black text-[#FFFF00] tracking-widest uppercase shadow">
            [ {{ sportsMatchup.league }} MATCHUP ON PREVUE ]
          </div>

          <!-- Center: Team Logos Split with VS Badge -->
          <div class="flex items-center justify-around w-full px-2 py-1">
            <!-- Away Team -->
            <div class="flex flex-col items-center space-y-1 w-[42%] text-center">
              <div class="w-10 h-10 sm:w-14 sm:h-14 flex items-center justify-center p-0.5" v-html="sportsMatchup.awayTeam.logoSvg"></div>
              <span class="text-[10px] sm:text-xs font-black text-[#FFFFFF] truncate w-full tracking-wider">
                {{ sportsMatchup.awayTeam.nickname || sportsMatchup.awayTeam.name }}
              </span>
              <span class="text-[8px] sm:text-[9px] text-[#00FFFF] font-bold uppercase truncate w-full">
                {{ sportsMatchup.awayTeam.city }}
              </span>
            </div>

            <!-- VS Badge -->
            <div class="flex flex-col items-center justify-center px-1">
              <span class="bg-[#FFFF00] text-[#000033] px-2 py-0.5 text-[10px] sm:text-xs font-black rounded-xs shadow-[0_0_8px_rgba(255,255,0,0.8)] animate-pulse">VS</span>
            </div>

            <!-- Home Team -->
            <div class="flex flex-col items-center space-y-1 w-[42%] text-center">
              <div class="w-10 h-10 sm:w-14 sm:h-14 flex items-center justify-center p-0.5" v-html="sportsMatchup.homeTeam.logoSvg"></div>
              <span class="text-[10px] sm:text-xs font-black text-[#FFFFFF] truncate w-full tracking-wider">
                {{ sportsMatchup.homeTeam.nickname || sportsMatchup.homeTeam.name }}
              </span>
              <span class="text-[8px] sm:text-[9px] text-[#00FFFF] font-bold uppercase truncate w-full">
                {{ sportsMatchup.homeTeam.city }}
              </span>
            </div>
          </div>

          <!-- Bottom Matchup Label -->
          <div class="w-full bg-[#000022] border-t border-[#333366] py-0.5 text-center text-[9px] sm:text-[10px] text-[#FFFF00] font-bold truncate px-1">
            {{ sportsMatchup.awayTeam.shortName }} AT {{ sportsMatchup.homeTeam.shortName }} // LIVE LOCAL COVERAGE
          </div>
        </div>

        <!-- Option 3: Standard Image Promo Box -->
        <div v-else-if="currentEvent?.image_url" class="w-full h-full relative">
          <img
            :src="currentEvent.image_url"
            :alt="currentEvent.title"
            class="w-full h-full object-cover opacity-90 transition-opacity duration-500"
            @error="handleImageError"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-[#000022] via-transparent to-transparent opacity-60"></div>
          <div class="absolute bottom-1.5 left-1.5 flex items-center space-x-1">
            <div class="bg-[#000080]/80 px-1.5 py-0.2 text-[10px] sm:text-xs text-[#00FFFF] border border-[#333366]">
              FEATURED
            </div>
            <div
              v-if="currentEvent?.has_ticket === 1"
              class="bg-[#00FF00] text-[#000033] px-1.5 py-0.2 text-[10px] sm:text-xs font-black border border-[#00FF00] shadow-[0_0_8px_rgba(0,255,0,0.8)]"
            >
              [TICKET HOLDER]
            </div>
          </div>
        </div>

        <!-- Option 4: Fallback Prevue Box -->
        <div v-else class="w-full h-full flex flex-col items-center justify-center p-2 sm:p-4 text-center bg-[#000055]">
          <div class="text-2xl sm:text-4xl font-black text-[#FFFF00] tracking-widest mb-1 sm:mb-2">PREVUE</div>
          <div class="text-[10px] sm:text-xs text-[#00FFFF] uppercase tracking-wider">{{ currentEvent?.category || 'SPOTLIGHT' }}</div>
          <div
            v-if="currentEvent?.has_ticket === 1"
            class="mt-1 sm:mt-2 bg-[#00FF00] text-[#000033] px-1.5 py-0.2 text-[10px] sm:text-xs font-black border border-[#00FF00]"
          >
            [TICKET HOLDER]
          </div>
        </div>
      </div>

      <!-- Right: Retro Bulletin Text Details -->
      <div class="w-[62%] sm:w-[55%] h-full flex flex-col justify-between py-0.5 pr-1 font-mono overflow-hidden">
        <div class="space-y-1 sm:space-y-1.5 overflow-hidden">
          <!-- Top Meta Tag -->
          <div class="flex items-center justify-between text-[10px] sm:text-xs border-b border-[#333366] pb-1">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="text-[#00FFFF] font-bold tracking-wider truncate">
                [ {{ currentEvent?.category?.toUpperCase() || 'EVENT' }} ]
              </span>
              <span
                v-if="currentEvent?.has_ticket === 1"
                class="bg-[#00FF00] text-[#000033] text-[9px] px-1 py-0.2 font-black rounded-xs shadow-[0_0_6px_rgba(0,255,0,0.8)] shrink-0"
              >
                [TICKET OWNED]
              </span>
            </div>
            <span class="text-[#8888AA] text-[9px] sm:text-[10px] shrink-0">
              {{ currentIndex + 1 }}/{{ featuredEvents.length }}
            </span>
          </div>

          <!-- Venue Name -->
          <div class="text-[11px] sm:text-xs text-[#E0E0E0] uppercase tracking-wide truncate">
            VENUE: <span class="text-[#FFFFFF] font-bold">{{ currentEvent?.venue_name || 'LOCAL VENUE' }}</span>
          </div>

          <!-- Event Title -->
          <div class="text-sm sm:text-base md:text-xl font-black text-[#FFFF00] leading-tight line-clamp-2 tracking-wide drop-shadow-md">
            {{ currentEvent?.title || 'NO FEATURED EVENTS SCHEDULED' }}
          </div>

          <!-- Date & Time -->
          <div class="text-[11px] sm:text-xs text-[#00FFFF] font-semibold truncate">
            DATE: <span class="text-[#FFFFFF]">{{ formattedDate }}</span>
          </div>

          <!-- Price Range -->
          <div class="text-[11px] sm:text-xs text-[#00FF00] font-semibold truncate">
            PRICE: <span class="text-[#E0E0E0]">{{ formattedPrice }}</span>
          </div>

          <!-- Description Snippet -->
          <p v-if="currentEvent?.description" class="text-[10px] sm:text-[11px] text-[#A0A0C0] line-clamp-1 sm:line-clamp-2 leading-relaxed pt-0.5">
            {{ currentEvent.description }}
          </p>
        </div>

        <!-- Bottom: Ticket QR & Action Bar -->
        <div class="flex items-center justify-between pt-1 border-t border-[#333366]">
          <div class="flex items-center space-x-2 sm:space-x-3">
            <div v-if="qrCodeDataUrl" class="bg-white p-0.5 sm:p-1 rounded-xs border border-[#FFFF00] shrink-0">
              <img :src="qrCodeDataUrl" alt="Ticket QR" class="w-7 h-7 sm:w-9 sm:h-9 object-contain" />
            </div>
            <div class="text-[9px] sm:text-[10px] text-[#8888AA] leading-tight hidden sm:block">
              <span class="text-[#FFFF00] font-bold block">SCAN FOR TICKETS</span>
              <span>DIRECT MOBILE CHECKOUT</span>
            </div>
          </div>

          <!-- Rotation Indicator Dots -->
          <div class="flex space-x-1 sm:space-x-1.5">
            <button
              v-for="(_, idx) in featuredEvents"
              :key="idx"
              class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full transition-all cursor-pointer"
              :class="idx === currentIndex ? 'bg-[#FFFF00] scale-125' : 'bg-[#333366] hover:bg-[#8888AA]'"
              @click="setIndex(idx)"
            ></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Overlayed Translucent Spotify Marquee Ticker (Bottom Divider Ribbon) -->
    <div class="w-full mt-2 bg-[#000022]/85 backdrop-blur-xs border-t border-b border-[#FFFF00]/50 px-2 py-0.5 flex items-center justify-between text-[10px] sm:text-[11px] font-mono text-[#E0E0E0] shadow-md shrink-0">
      <!-- Left: Animated Equalizer & Brand -->
      <div class="flex items-center space-x-2 shrink-0">
        <span class="w-2 h-2 bg-[#1DB954] rounded-full inline-block animate-pulse shadow-[0_0_6px_#1DB954]"></span>
        <span class="text-[#1DB954] font-black tracking-wider hidden sm:inline">[ SPOTIFY MUZAK ]</span>
        <div class="flex items-end space-x-0.5 h-3 text-[#1DB954]">
          <span class="w-0.5 bg-[#1DB954] animate-pulse h-2"></span>
          <span class="w-0.5 bg-[#1DB954] animate-pulse h-3"></span>
          <span class="w-0.5 bg-[#1DB954] animate-pulse h-1.5"></span>
          <span class="w-0.5 bg-[#1DB954] animate-pulse h-2.5"></span>
        </div>
      </div>

      <!-- Center: Scrolling Retro Track / Audio Info Marquee -->
      <div class="flex-1 mx-3 overflow-hidden whitespace-nowrap text-center">
        <span class="text-[#FFFF00] font-bold tracking-wide animate-pulse inline-block">
          NOW STREAMING: {{ currentMuzakTrack }} // 12 kHz HIGH-SHELF RF HEADEND FILTER ENGAGED
        </span>
      </div>

      <!-- Right: Playlist Launcher Link -->
      <div class="flex items-center space-x-2 shrink-0">
        <a
          href="https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f"
          target="_blank"
          rel="noopener noreferrer"
          class="bg-[#1DB954] text-[#000033] hover:bg-white px-2 py-0.5 font-black text-[9px] sm:text-[10px] tracking-wider transition-all cursor-pointer shadow-[0_0_6px_rgba(29,185,84,0.6)]"
        >
          [ OPEN SPOTIFY ]
        </a>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { parseSportsMatchup } from '../services/sportsAssets'
import { commercialsEngine } from '../services/commercialsEngine'
import type { EventItem } from '../types'

const props = defineProps<{
  events: EventItem[]
  rotationSeconds?: number
}>()

const currentIndex = ref(0)
const qrCodeDataUrl = ref<string>('')
let timer: ReturnType<typeof setInterval> | null = null

// Spotify Marquee Track Playlist Simulation
const spotifyTracks = [
  "OPENPREVUE CABLE HEADEND JAZZ",
  "WEATHER CHANNEL 1995 RADAR LOUNGE",
  "PREVUE CHANNEL AUTOSCROLL THEME",
  "COMPOSITE RF 12kHz SMOOTH VAPOR",
  "VINTAGE NTSC BROADCAST AUDIO"
]
const trackIndex = ref(0)
let trackTimer: ReturnType<typeof setInterval> | null = null

const currentMuzakTrack = computed(() => {
  return spotifyTracks[trackIndex.value % spotifyTracks.length]
})

const featuredEvents = computed(() => {
  const featured = props.events.filter(e => e.is_featured === 1)
  return featured.length > 0 ? featured : props.events.slice(0, 5)
})

const currentEvent = computed(() => {
  if (featuredEvents.value.length === 0) return null
  return featuredEvents.value[currentIndex.value % featuredEvents.value.length]
})

const sportsMatchup = computed(() => {
  if (!currentEvent.value) return null
  return parseSportsMatchup(currentEvent.value.title)
})

const formattedDate = computed(() => {
  if (!currentEvent.value?.start_time) return 'TBA'
  try {
    const d = new Date(currentEvent.value.start_time)
    return d.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch {
    return currentEvent.value.start_time
  }
})

const formattedPrice = computed(() => {
  if (!currentEvent.value) return 'TBA'
  const { price_min, price_max, currency } = currentEvent.value
  if (price_min !== undefined && price_min !== null && price_max !== undefined && price_max !== null) {
    if (price_min === price_max) return `$${price_min.toFixed(2)} ${currency}`
    return `$${price_min.toFixed(2)} - $${price_max.toFixed(2)} ${currency}`
  }
  if (price_min !== undefined && price_min !== null) return `From $${price_min.toFixed(2)}`
  return 'Check Box Office'
})

async function generateQr(url: string) {
  try {
    qrCodeDataUrl.value = await QRCode.toDataURL(url, {
      margin: 1,
      width: 56,
      color: {
        dark: '#000033',
        light: '#FFFFFF',
      },
    })
  } catch {
    qrCodeDataUrl.value = ''
  }
}

function handleImageError(e: Event) {
  const target = e.target as HTMLImageElement
  if (target && currentEvent.value) {
    target.style.display = 'none'
  }
}

function setIndex(idx: number) {
  currentIndex.value = idx
}

function startRotation() {
  if (timer) clearInterval(timer)
  const interval = (props.rotationSeconds || 20) * 1000
  timer = setInterval(() => {
    if (featuredEvents.value.length > 0) {
      currentIndex.value = (currentIndex.value + 1) % featuredEvents.value.length
    }
  }, interval)
}

watch(currentEvent, (evt) => {
  if (evt?.ticket_url) {
    generateQr(evt.ticket_url)
  } else {
    qrCodeDataUrl.value = ''
  }
}, { immediate: true })

onMounted(() => {
  startRotation()
  commercialsEngine.startTimer()
  trackTimer = setInterval(() => {
    trackIndex.value = (trackIndex.value + 1) % spotifyTracks.length
  }, 12000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (trackTimer) clearInterval(trackTimer)
  commercialsEngine.stopTimer()
})
</script>
