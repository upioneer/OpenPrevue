<template>
  <div class="h-[45%] w-full bg-gradient-to-b from-[#000088] via-[#000044] to-[#000022] border-b-2 border-[#FFFF00] p-3 flex gap-4 overflow-hidden select-none">
    <!-- Left: Event Promo Media Box -->
    <div class="w-[45%] h-full flex flex-col items-center justify-center bg-[#000022] border-2 border-[#333366] rounded-sm overflow-hidden relative shadow-inner">
      <div v-if="currentEvent?.image_url" class="w-full h-full relative">
        <img
          :src="currentEvent.image_url"
          :alt="currentEvent.title"
          class="w-full h-full object-cover opacity-90 transition-opacity duration-500"
          @error="handleImageError"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-[#000022] via-transparent to-transparent opacity-60"></div>
        <div class="absolute bottom-2 left-2 flex items-center space-x-1.5">
          <div class="bg-[#000080]/80 px-2 py-0.5 text-xs text-[#00FFFF] border border-[#333366]">
            FEATURED EVENT
          </div>
          <div
            v-if="currentEvent?.has_ticket === 1"
            class="bg-[#00FF00] text-[#000033] px-2 py-0.5 text-xs font-black border border-[#00FF00] shadow-[0_0_8px_rgba(0,255,0,0.8)]"
          >
            [TICKET HOLDER]
          </div>
        </div>
      </div>
      <div v-else class="w-full h-full flex flex-col items-center justify-center p-4 text-center bg-[#000055]">
        <div class="text-4xl font-black text-[#FFFF00] tracking-widest mb-2">PREVUE</div>
        <div class="text-xs text-[#00FFFF] uppercase tracking-wider">{{ currentEvent?.category || 'SPOTLIGHT' }}</div>
        <div
          v-if="currentEvent?.has_ticket === 1"
          class="mt-2 bg-[#00FF00] text-[#000033] px-2 py-0.5 text-xs font-black border border-[#00FF00]"
        >
          [TICKET HOLDER]
        </div>
      </div>
    </div>

    <!-- Right: Retro Bulletin Text Details -->
    <div class="w-[55%] h-full flex flex-col justify-between py-1 pr-2 font-mono">
      <div class="space-y-2 overflow-hidden">
        <!-- Top Meta Tag -->
        <div class="flex items-center justify-between text-xs border-b border-[#333366] pb-1">
          <div class="flex items-center space-x-2">
            <span class="text-[#00FFFF] font-bold tracking-wider">
              [ {{ currentEvent?.category?.toUpperCase() || 'EVENT' }} ]
            </span>
            <span
              v-if="currentEvent?.has_ticket === 1"
              class="bg-[#00FF00] text-[#000033] text-[10px] px-1.5 py-0.2 font-black rounded-xs shadow-[0_0_6px_rgba(0,255,0,0.8)]"
            >
              [TICKET OWNED]
            </span>
          </div>
          <span class="text-[#8888AA] text-[10px]">
            SPOTLIGHT {{ currentIndex + 1 }} OF {{ featuredEvents.length }}
          </span>
        </div>

        <!-- Venue Name -->
        <div class="text-xs text-[#E0E0E0] uppercase tracking-wide">
          VENUE: <span class="text-[#FFFFFF] font-bold">{{ currentEvent?.venue_name || 'LOCAL VENUE' }}</span>
        </div>

        <!-- Event Title -->
        <div class="text-lg md:text-xl font-black text-[#FFFF00] leading-tight line-clamp-2 tracking-wide drop-shadow-md">
          {{ currentEvent?.title || 'NO FEATURED EVENTS SCHEDULED' }}
        </div>

        <!-- Date & Time -->
        <div class="text-xs text-[#00FFFF] font-semibold">
          DATE: <span class="text-[#FFFFFF]">{{ formattedDate }}</span>
        </div>

        <!-- Price Range -->
        <div class="text-xs text-[#00FF00] font-semibold">
          PRICE: <span class="text-[#E0E0E0]">{{ formattedPrice }}</span>
        </div>

        <!-- Description Snippet -->
        <p v-if="currentEvent?.description" class="text-[11px] text-[#A0A0C0] line-clamp-2 leading-relaxed pt-1">
          {{ currentEvent.description }}
        </p>
      </div>

      <!-- Bottom: Ticket QR & Action Bar -->
      <div class="flex items-center justify-between pt-2 border-t border-[#333366]">
        <div class="flex items-center space-x-3">
          <div v-if="qrCodeDataUrl" class="bg-white p-1 rounded-xs border border-[#FFFF00]">
            <img :src="qrCodeDataUrl" alt="Ticket QR" class="w-12 h-12 object-contain" />
          </div>
          <div class="text-[10px] text-[#8888AA] leading-tight">
            <span class="text-[#FFFF00] font-bold block">SCAN FOR TICKETS</span>
            <span>DIRECT MOBILE CHECKOUT</span>
          </div>
        </div>

        <!-- Rotation Indicator Dots -->
        <div class="flex space-x-1.5">
          <button
            v-for="(_, idx) in featuredEvents"
            :key="idx"
            class="w-2 h-2 rounded-full transition-all"
            :class="idx === currentIndex ? 'bg-[#FFFF00] scale-125' : 'bg-[#333366] hover:bg-[#8888AA]'"
            @click="setIndex(idx)"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import type { EventItem } from '../types'

const props = defineProps<{
  events: EventItem[]
  rotationSeconds?: number
}>()

const currentIndex = ref(0)
const qrCodeDataUrl = ref<string>('')
let timer: ReturnType<typeof setInterval> | null = null

const featuredEvents = computed(() => {
  const featured = props.events.filter(e => e.is_featured === 1)
  return featured.length > 0 ? featured : props.events.slice(0, 5)
})

const currentEvent = computed(() => {
  if (featuredEvents.value.length === 0) return null
  return featuredEvents.value[currentIndex.value % featuredEvents.value.length]
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
      width: 64,
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
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
