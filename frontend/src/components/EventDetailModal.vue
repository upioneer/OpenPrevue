<template>
  <div
    v-if="isOpen && event"
    class="fixed inset-0 z-50 bg-[#000022]/85 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto select-none font-mono"
    @click.self="handleBackdropClick"
    @keydown.esc="closeModal"
  >
    <div
      class="w-full max-w-2xl bg-[#000033] border-2 border-[#FFFF00] shadow-[0_0_30px_rgba(255,255,0,0.35)] text-[#E0E0E0] flex flex-col overflow-hidden relative rounded-xs my-auto max-h-[92vh]"
      role="dialog"
      aria-modal="true"
    >
      <!-- Auto-Close Depletion Progress Bar -->
      <div class="w-full h-1 bg-[#000055] overflow-hidden shrink-0">
        <div
          class="h-full transition-all duration-200 ease-linear"
          :class="persistUntilClosed ? 'bg-[#00FFFF]' : 'bg-[#FFFF00]'"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <!-- Retro Modal Header -->
      <div class="h-10 bg-[#000066] border-b-2 border-[#333366] flex items-center justify-between px-3 sm:px-4 shrink-0">
        <div class="flex items-center space-x-2 truncate">
          <span
            class="rounded-full inline-block w-2.5 h-2.5 shrink-0 shadow-[0_0_4px_currentColor]"
            :class="getCategoryColor(event.category)"
          ></span>
          <span class="font-black text-xs sm:text-sm text-[#FFFF00] tracking-wider uppercase truncate">
            [ {{ getCategoryHeader(event.category) }} ]
          </span>
        </div>

        <div class="flex items-center space-x-2 shrink-0">
          <!-- Countdown Badge -->
          <span
            class="text-[10px] sm:text-xs font-black uppercase px-2 py-0.5 border rounded-xs"
            :class="persistUntilClosed
              ? 'bg-[#000044] text-[#00FFFF] border-[#00FFFF]'
              : 'bg-[#000044] text-[#FFFF00] border-[#FFFF00] animate-pulse'"
          >
            {{ persistUntilClosed ? '[ PERSISTENT MODE ]' : `[ AUTO-CLOSES IN ${remainingSeconds}S ]` }}
          </span>

          <!-- Close Button -->
          <button
            type="button"
            class="text-xs sm:text-sm font-black px-2 py-0.5 border border-[#FFFF00] text-[#FFFF00] bg-[#000044] hover:bg-[#FFFF00] hover:text-[#000033] cursor-pointer transition-colors uppercase"
            title="Close dialog (Escape)"
            @click="closeModal"
          >
            [ X ]
          </button>
        </div>
      </div>

      <!-- Modal Body (Scrollable for smaller screens) -->
      <div class="p-3 sm:p-5 overflow-y-auto space-y-4 max-h-[calc(92vh-110px)] scrollbar-thin">
        <!-- 1. Graphics Presentation: Sports VS Card OR Event Artwork -->
        <div v-if="isSportsCategory && matchupTeams" class="border border-[#00FFFF]/50 bg-[#000022] p-3 rounded-xs shadow-inner">
          <div class="flex items-center justify-between border-b border-[#00FFFF]/30 pb-1 mb-2 text-xs">
            <div class="flex items-center space-x-1.5 truncate">
              <img
                v-if="leagueBranding?.logoUrl"
                :src="leagueBranding.logoUrl"
                :alt="leagueBranding.shortName"
                class="h-4 w-auto object-contain bg-white/10 px-1 py-0.5 rounded-xs shrink-0"
              />
              <span class="text-[#FFFF00] font-black uppercase tracking-wider">
                {{ leagueBranding?.shortName ? leagueBranding.shortName + ' LIVE MATCHUP' : 'HEAD TO HEAD MATCHUP' }}
              </span>
            </div>
            <span class="text-[#00FFFF] font-bold text-xs uppercase truncate max-w-[200px]">
              {{ event.venue_name || 'MAIN ARENA' }}
            </span>
          </div>

          <div class="flex flex-col sm:flex-row items-center justify-around py-2 text-center w-full gap-2 sm:gap-0">
            <!-- Team A -->
            <div class="flex sm:flex-col flex-row items-center space-x-3 sm:space-x-0 sm:space-y-1 w-full sm:w-[42%] justify-center sm:justify-start">
              <div
                class="w-14 h-14 sm:w-20 sm:h-20 rounded-full border-2 sm:border-3 p-1.5 sm:p-2 flex items-center justify-center font-black relative overflow-hidden shadow-lg shrink-0"
                :style="{
                  borderColor: teamABranding?.secondaryColor || '#FFFF00',
                  backgroundColor: teamABranding?.primaryColor || '#000044',
                  boxShadow: `0 0 14px ${teamABranding?.secondaryColor || 'rgba(255,255,0,0.5)'}`
                }"
              >
                <img
                  v-if="teamABranding?.logoUrl && !teamALogoError"
                  :src="teamABranding.logoUrl"
                  :alt="teamABranding.name"
                  referrerpolicy="no-referrer"
                  class="w-full h-full object-contain drop-shadow"
                  @error="teamALogoError = true"
                />
                <div
                  v-else-if="teamABranding?.logoSvg"
                  class="w-full h-full flex items-center justify-center p-1"
                  v-html="teamABranding.logoSvg"
                ></div>
                <span
                  v-else
                  class="font-black text-lg sm:text-xl"
                  :style="{ color: teamABranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamABranding?.shortName || matchupTeams.teamA.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm font-black text-[#FFFFFF] truncate w-auto sm:w-full uppercase text-left sm:text-center">
                {{ teamABranding?.name || matchupTeams.teamA }}
              </span>
            </div>

            <!-- VS Badge -->
            <div class="flex sm:flex-col flex-row items-center justify-center space-x-2 sm:space-x-0 shrink-0 px-2 py-0.5">
              <span class="font-black text-lg sm:text-2xl text-[#FF4444] animate-pulse drop-shadow-[0_0_10px_rgba(255,68,68,0.9)]">
                VS
              </span>
              <span class="text-[9px] text-[#00FFFF] font-black tracking-widest uppercase">MATCHUP</span>
            </div>

            <!-- Team B -->
            <div class="flex sm:flex-col flex-row items-center space-x-3 sm:space-x-0 sm:space-y-1 w-full sm:w-[42%] justify-center sm:justify-start">
              <div
                class="w-14 h-14 sm:w-20 sm:h-20 rounded-full border-2 sm:border-3 p-1.5 sm:p-2 flex items-center justify-center font-black relative overflow-hidden shadow-lg shrink-0"
                :style="{
                  borderColor: teamBBranding?.secondaryColor || '#00FFFF',
                  backgroundColor: teamBBranding?.primaryColor || '#000044',
                  boxShadow: `0 0 14px ${teamBBranding?.secondaryColor || 'rgba(0,255,255,0.5)'}`
                }"
              >
                <img
                  v-if="teamBBranding?.logoUrl && !teamBLogoError"
                  :src="teamBBranding.logoUrl"
                  :alt="teamBBranding.name"
                  referrerpolicy="no-referrer"
                  class="w-full h-full object-contain drop-shadow"
                  @error="teamBLogoError = true"
                />
                <div
                  v-else-if="teamBBranding?.logoSvg"
                  class="w-full h-full flex items-center justify-center p-1"
                  v-html="teamBBranding.logoSvg"
                ></div>
                <span
                  v-else
                  class="font-black text-lg sm:text-xl"
                  :style="{ color: teamBBranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamBBranding?.shortName || matchupTeams.teamB.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm font-black text-[#FFFFFF] truncate w-auto sm:w-full uppercase text-left sm:text-center">
                {{ teamBBranding?.name || matchupTeams.teamB }}
              </span>
            </div>
          </div>
        </div>

        <!-- 2. Non-Sports Event Poster Artwork or Genre Banner -->
        <div v-else-if="event.image_url && !imageError" class="relative w-full h-44 sm:h-52 bg-[#000022] border border-[#333366] rounded-xs overflow-hidden">
          <img
            :src="event.image_url"
            :alt="event.title"
            class="w-full h-full object-cover"
            @error="imageError = true"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-[#000033] via-transparent to-transparent"></div>
          <div class="absolute bottom-2 left-2 right-2 flex items-center justify-between">
            <span class="text-xs font-black bg-[#000022]/90 border border-[#00FFFF] text-[#00FFFF] px-2 py-0.5 rounded-xs uppercase">
              {{ event.category }}
            </span>
            <span v-if="event.source" class="text-xs font-black bg-[#000022]/90 border border-[#FFFF00] text-[#FFFF00] px-2 py-0.5 rounded-xs uppercase">
              {{ event.source }}
            </span>
          </div>
        </div>

        <!-- 3. Event Title and Core Metadata -->
        <div class="space-y-1">
          <h2 class="text-base sm:text-lg md:text-xl font-black text-[#FFFF00] leading-snug tracking-wide uppercase">
            {{ displayTitle }}
          </h2>
          <div class="text-xs sm:text-sm text-[#00FFFF] font-bold flex items-center space-x-2 truncate uppercase">
            <span>{{ event.venue_name || 'LOCAL VENUE' }}</span>
            <span v-if="event.venue_city" class="text-[#8888AA]">• {{ event.venue_city }}{{ event.venue_state ? `, ${event.venue_state}` : '' }}</span>
          </div>
        </div>

        <!-- 4. Schedule & Price Cards Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm">
          <!-- Date & Time Box -->
          <div class="bg-[#000022] border border-[#333366] p-2.5 rounded-xs space-y-1">
            <div class="text-[#8888AA] text-[10px] sm:text-xs font-black uppercase tracking-wider">DATE & TIME</div>
            <div class="text-[#FFFFFF] font-black text-xs sm:text-sm">{{ formattedFullDate }}</div>
            <div class="text-[#00FFFF] font-bold text-xs">{{ formattedStartTime }}</div>
          </div>

          <!-- Price & Ticket Status Box -->
          <div class="bg-[#000022] border border-[#333366] p-2.5 rounded-xs space-y-1">
            <div class="text-[#8888AA] text-[10px] sm:text-xs font-black uppercase tracking-wider">ADMISSION & COMMITMENT</div>
            <div class="text-[#FFFF00] font-black text-xs sm:text-sm">{{ formattedPrice }}</div>
            <div class="flex items-center space-x-2">
              <span
                class="text-[10px] font-black px-1.5 py-0.2 rounded-xs border"
                :class="event.has_ticket === 1
                  ? 'bg-[#00FF00]/20 text-[#00FF00] border-[#00FF00]'
                  : 'bg-[#444466]/20 text-[#8888AA] border-[#444466]'"
              >
                {{ event.has_ticket === 1 ? '[ TICKET OWNED ]' : '[ NO TICKET LOGGED ]' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 5. Description / Synopsis Box -->
        <div v-if="event.description" class="bg-[#000022] border border-[#333366] p-2.5 rounded-xs space-y-1">
          <div class="text-[#8888AA] text-[10px] sm:text-xs font-black uppercase tracking-wider">EVENT DETAILS & SYNOPSIS</div>
          <p class="text-xs sm:text-sm text-[#CCCCCC] leading-relaxed whitespace-pre-line max-h-32 overflow-y-auto scrollbar-thin">
            {{ event.description }}
          </p>
        </div>

        <!-- 6. Mobile QR Code & External Ticket Access -->
        <div v-if="qrCodeDataUrl" class="bg-[#000022] border border-[#333366] p-2.5 rounded-xs flex items-center space-x-3">
          <img
            :src="qrCodeDataUrl"
            alt="Ticket QR Code"
            class="w-16 h-16 sm:w-20 sm:h-20 bg-white p-1 rounded-xs border border-[#444466] shrink-0"
          />
          <div class="flex-1 min-w-0 space-y-1">
            <div class="text-[10px] sm:text-xs font-black text-[#00FFFF] uppercase tracking-wider flex items-center justify-between">
              <span>{{ event.has_ticket === 1 ? '[ SCAN FOR DIGITAL PASS / REVIEW ]' : '[ SCAN FOR HOST / BOX OFFICE ]' }}</span>
              <span v-if="vendorDomain" class="text-[#FFFF00] text-[9px] uppercase font-bold border border-[#FFFF00]/40 px-1 py-0.2 rounded-xs">
                {{ vendorDomain }}
              </span>
            </div>
            <p class="text-[11px] sm:text-xs text-[#CCCCCC] leading-tight">
              {{ event.has_ticket === 1
                ? 'Scan with your mobile camera to review your purchased tickets, access digital barcode passes, or manage your reservation directly with the host vendor.'
                : 'Scan with your mobile camera to purchase official event tickets or review admission details directly on the host vendor website.'
              }}
            </p>
            <a
              v-if="event.ticket_url"
              :href="event.ticket_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-block text-[11px] sm:text-xs font-black text-[#FFFF00] hover:underline uppercase"
            >
              [ OPEN {{ vendorDomain || 'TICKET LINK' }} IN BROWSER ]
            </a>
          </div>
        </div>

        <!-- 7. Delete Confirmation Dialog Overlay / In-Modal State -->
        <div
          v-if="showDeleteConfirm"
          class="border-2 border-[#FF0000] bg-[#330000] p-3 sm:p-4 rounded-xs space-y-2.5 shadow-[0_0_20px_rgba(255,0,0,0.5)]"
        >
          <div class="flex items-center space-x-2 text-[#FF4444] font-black text-xs sm:text-sm uppercase tracking-wider">
            <span class="w-2.5 h-2.5 bg-[#FF0000] rounded-full animate-ping inline-block shrink-0"></span>
            <span>CONFIRM EVENT DELETION</span>
          </div>
          <p class="text-xs sm:text-sm text-[#FFFFFF] leading-snug">
            Are you sure you want to permanently remove <strong class="text-[#FFFF00]">"{{ displayTitle }}"</strong> from the OpenPrevue broadcast schedule? This action cannot be undone.
          </p>
          <div class="flex items-center space-x-2 pt-1">
            <button
              type="button"
              :disabled="isDeleting"
              class="px-3 py-1.5 bg-[#FF0000] hover:bg-[#FF3333] text-white font-black text-xs uppercase rounded-xs cursor-pointer border border-[#FF6666] transition-colors disabled:opacity-50"
              @click="confirmDelete"
            >
              {{ isDeleting ? '[ DELETING... ]' : '[ CONFIRM DELETE ]' }}
            </button>
            <button
              type="button"
              :disabled="isDeleting"
              class="px-3 py-1.5 bg-[#000044] hover:bg-[#000066] text-[#E0E0E0] font-black text-xs uppercase rounded-xs cursor-pointer border border-[#444466] transition-colors"
              @click="showDeleteConfirm = false"
            >
              [ CANCEL ]
            </button>
          </div>
        </div>

        <!-- 8. Interactive Action Buttons -->
        <div v-else class="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-[#333366]">
          <div class="flex flex-wrap items-center gap-2">
            <!-- Ticket Commitment Toggle Button -->
            <button
              type="button"
              class="px-2.5 py-1 text-xs font-black uppercase rounded-xs border cursor-pointer transition-colors"
              :class="event.has_ticket === 1
                ? 'bg-[#00FF00] text-[#000033] border-[#00FF00] hover:bg-[#66FF66]'
                : 'bg-[#000044] text-[#8888AA] border-[#444466] hover:text-[#00FFFF] hover:border-[#00FFFF]'"
              @click="toggleTicketCommitment"
            >
              {{ event.has_ticket === 1 ? '[ TICKET OWNED ]' : '[ + CLAIM TICKET ]' }}
            </button>

            <!-- External Ticket URL Button -->
            <a
              v-if="event.ticket_url"
              :href="event.ticket_url"
              target="_blank"
              rel="noopener noreferrer"
              class="px-2.5 py-1 text-xs font-black uppercase rounded-xs border border-[#00FFFF] bg-[#000044] text-[#00FFFF] hover:bg-[#00FFFF] hover:text-[#000033] cursor-pointer transition-colors"
            >
              {{ event.has_ticket === 1 ? '[ REVIEW PASSES ]' : '[ BOX OFFICE ]' }}
            </a>
          </div>

          <!-- Danger Delete Button -->
          <button
            type="button"
            class="px-2.5 py-1 text-xs font-black uppercase rounded-xs border border-[#FF4444] text-[#FF4444] bg-[#000022] hover:bg-[#FF0000] hover:text-[#FFFFFF] cursor-pointer transition-colors shrink-0"
            @click="showDeleteConfirm = true"
          >
            [ DELETE EVENT ]
          </button>
        </div>
      </div>

      <!-- Retro Modal Footer Bar -->
      <div class="h-10 bg-[#000044] border-t-2 border-[#333366] flex items-center justify-between px-3 sm:px-4 shrink-0">
        <!-- Persistent Mode Checkbox -->
        <label class="flex items-center space-x-2 cursor-pointer text-xs sm:text-sm text-[#00FFFF] hover:text-[#FFFF00] font-black uppercase select-none">
          <input
            type="checkbox"
            v-model="persistUntilClosed"
            class="sr-only"
            @change="handlePersistToggle"
          />
          <span class="font-mono text-xs sm:text-sm">
            [ {{ persistUntilClosed ? 'X' : ' ' }} ]
          </span>
          <span class="text-[11px] sm:text-xs">
            KEEP OPEN (DISABLE 30S AUTO-CLOSE)
          </span>
        </label>

        <!-- Dismiss Button -->
        <button
          type="button"
          class="text-xs font-black px-2.5 py-0.5 border border-[#444466] text-[#E0E0E0] bg-[#000022] hover:bg-[#000066] hover:text-[#FFFF00] cursor-pointer transition-colors uppercase rounded-xs"
          @click="closeModal"
        >
          [ CLOSE ]
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import {
  cleanEventTitle,
  parseMatchup,
  resolveLeagueBranding,
  resolveTeamBranding
} from '../services/sportsTheme'
import { deleteEvent, updateEvent } from '../api/client'
import type { EventItem } from '../types'

const props = defineProps<{
  isOpen: boolean
  event: EventItem | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'eventDeleted', eventId: string): void
  (e: 'eventUpdated', event: EventItem): void
}>()

const remainingSeconds = ref(30)
const persistUntilClosed = ref(false)
const showDeleteConfirm = ref(false)
const isDeleting = ref(false)
const qrCodeDataUrl = ref<string | null>(null)
const teamALogoError = ref(false)
const teamBLogoError = ref(false)
const imageError = ref(false)

let autoCloseInterval: ReturnType<typeof setInterval> | null = null

const progressPercent = computed(() => {
  if (persistUntilClosed.value) return 100
  return Math.max(0, Math.min(100, (remainingSeconds.value / 30) * 100))
})

const isSportsCategory = computed(() => {
  if (!props.event) return false
  const cat = (props.event.category || '').toLowerCase()
  return cat === 'sports' || cat.includes('sport') || cat === 'nba' || cat === 'nfl' || cat === 'mlb' || cat === 'nhl'
})

const matchupTeams = computed(() => {
  if (!props.event) return null
  return parseMatchup(props.event.title)
})

const teamABranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamA)
})

const teamBBranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamB)
})

const leagueBranding = computed(() => {
  if (!matchupTeams.value?.league) return null
  return resolveLeagueBranding(matchupTeams.value.league)
})

const displayTitle = computed(() => {
  if (!props.event) return ''
  return cleanEventTitle(props.event.title)
})

const formattedFullDate = computed(() => {
  if (!props.event?.start_time) return 'TBA'
  try {
    const d = new Date(props.event.start_time)
    return d.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }).toUpperCase()
  } catch {
    return props.event.start_time
  }
})

const formattedStartTime = computed(() => {
  if (!props.event?.start_time) return 'TBA'
  try {
    const d = new Date(props.event.start_time)
    return d.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short'
    }).toUpperCase()
  } catch {
    return ''
  }
})

const formattedPrice = computed(() => {
  if (!props.event) return 'FREE / GENERAL ADMISSION'
  if (props.event.price_min != null && props.event.price_max != null) {
    if (props.event.price_min === props.event.price_max) {
      return `$${props.event.price_min.toFixed(2)} ${props.event.currency || 'USD'}`
    }
    return `$${props.event.price_min.toFixed(2)} - $${props.event.price_max.toFixed(2)} ${props.event.currency || 'USD'}`
  }
  if (props.event.price_min != null) {
    return `FROM $${props.event.price_min.toFixed(2)} ${props.event.currency || 'USD'}`
  }
  return 'GENERAL ADMISSION'
})

const vendorDomain = computed(() => {
  const rawUrl = props.event?.ticket_url || props.event?.ticket_links?.[0]?.url
  if (!rawUrl) return null
  try {
    const parsed = new URL(rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`)
    return parsed.hostname.replace(/^www\./, '').toUpperCase()
  } catch {
    return null
  }
})

function getCategoryColor(category?: string): string {
  const cat = (category || '').toLowerCase()
  if (cat.includes('sport') || cat === 'nba' || cat === 'nfl') return 'bg-[#00FF00] text-[#00FF00]'
  if (cat.includes('concert') || cat.includes('music')) return 'bg-[#FF00FF] text-[#FF00FF]'
  if (cat.includes('theatre') || cat.includes('stage') || cat.includes('broadway')) return 'bg-[#FFFF00] text-[#FFFF00]'
  if (cat.includes('comedy')) return 'bg-[#FFA500] text-[#FFA500]'
  if (cat.includes('movie') || cat.includes('film')) return 'bg-[#00FFFF] text-[#00FFFF]'
  return 'bg-[#00FFFF] text-[#00FFFF]'
}

function getCategoryHeader(category?: string): string {
  const cat = (category || '').toLowerCase()
  if (cat.includes('sport') || cat === 'nba' || cat === 'nfl') return 'SPORTS MATCHUP'
  if (cat.includes('concert') || cat.includes('music')) return 'CONCERT / LIVE MUSIC'
  if (cat.includes('theatre') || cat.includes('stage') || cat.includes('broadway')) return 'STAGE & THEATRE'
  if (cat.includes('comedy')) return 'COMEDY EVENT'
  if (cat.includes('movie') || cat.includes('film')) return 'FILM & CINEMA'
  return category?.toUpperCase() || 'SCHEDULED EVENT'
}

function startTimer() {
  stopTimer()
  if (persistUntilClosed.value) return

  remainingSeconds.value = 30
  autoCloseInterval = setInterval(() => {
    if (persistUntilClosed.value) {
      stopTimer()
      return
    }
    remainingSeconds.value -= 1
    if (remainingSeconds.value <= 0) {
      stopTimer()
      closeModal()
    }
  }, 1000)
}

function stopTimer() {
  if (autoCloseInterval) {
    clearInterval(autoCloseInterval)
    autoCloseInterval = null
  }
}

function handlePersistToggle() {
  if (persistUntilClosed.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

function closeModal() {
  stopTimer()
  showDeleteConfirm.value = false
  emit('close')
}

function handleBackdropClick() {
  closeModal()
}

async function generateQrCode() {
  qrCodeDataUrl.value = null
  let url = props.event?.ticket_url || props.event?.ticket_links?.[0]?.url
  if (!url) return

  if (url.includes('openprevue.tv')) {
    url = url.replace('openprevue.tv', 'openprevue.com')
  }

  try {
    qrCodeDataUrl.value = await QRCode.toDataURL(url, {
      width: 160,
      margin: 1,
      color: {
        dark: '#000033',
        light: '#FFFFFF'
      }
    })
  } catch {
    qrCodeDataUrl.value = null
  }
}

async function toggleTicketCommitment() {
  if (!props.event) return
  const newStatus = props.event.has_ticket === 1 ? 0 : 1
  try {
    const updated = await updateEvent(props.event.id, { has_ticket: newStatus })
    props.event.has_ticket = newStatus
    emit('eventUpdated', updated)
  } catch {
    // Keep local toggle
    props.event.has_ticket = newStatus
  }
}

async function confirmDelete() {
  if (!props.event) return
  isDeleting.value = true
  const eventId = props.event.id
  try {
    await deleteEvent(eventId)
    emit('eventDeleted', eventId)
    closeModal()
  } catch (err: any) {
    alert(`Failed to delete event: ${err.message || err}`)
  } finally {
    isDeleting.value = false
    showDeleteConfirm.value = false
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.isOpen) {
    closeModal()
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open && props.event) {
      teamALogoError.value = false
      teamBLogoError.value = false
      imageError.value = false
      showDeleteConfirm.value = false
      isDeleting.value = false
      persistUntilClosed.value = false
      generateQrCode()
      startTimer()
    } else {
      stopTimer()
    }
  },
  { immediate: true }
)

watch(
  () => props.event,
  () => {
    if (props.isOpen && props.event) {
      teamALogoError.value = false
      teamBLogoError.value = false
      imageError.value = false
      showDeleteConfirm.value = false
      generateQrCode()
      startTimer()
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('keydown', handleKeyDown)
})
</script>
