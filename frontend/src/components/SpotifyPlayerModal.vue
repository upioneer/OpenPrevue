<template>
  <div>
    <!-- FULL MODAL OVERLAY (EXPANDED MODE) -->
    <div
      v-show="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 select-none font-mono transition-opacity duration-200"
      @click.self="minimize"
    >
      <div
        class="w-full max-w-xl bg-gradient-to-b from-[#000088] via-[#000055] to-[#000022] border-2 border-[#1DB954] rounded-xs shadow-[0_0_24px_rgba(29,185,84,0.6)] overflow-hidden flex flex-col"
      >
        <!-- Top Title Bar -->
        <div class="bg-[#0000AA] border-b-2 border-[#1DB954] px-4 py-2 flex items-center justify-between shrink-0">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 bg-[#1DB954] inline-block animate-pulse"></span>
            <span class="text-sm font-black text-[#1DB954] tracking-widest uppercase">
              [ SPOTIFY HEADEND AUDIO PLAYER ]
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <button
              type="button"
              class="text-xs text-[#00FFFF] hover:text-[#FFFFFF] border border-[#00FFFF] px-2 py-0.5 font-bold cursor-pointer transition-colors"
              @click="minimize"
              title="Keep music playing in background and return to guide"
            >
              [ MINIMIZE TO GUIDE ]
            </button>
          </div>
        </div>

        <!-- Body Content -->
        <div class="p-4 sm:p-5 space-y-4 text-xs">
          <div class="bg-[#000033] border border-[#333366] p-3 text-[#E0E0E0] leading-relaxed space-y-1">
            <div class="text-[#FFFF00] font-black uppercase flex items-center justify-between">
              <span>PLAYLIST: "{{ playlistTitle }}" {{ playlistAuthor ? 'BY ' + playlistAuthor.toUpperCase() : '' }}</span>
              <span class="text-[#1DB954] text-[11px]">[ LIVE SPOTIFY SYNC ]</span>
            </div>
            <p class="text-[11px] text-[#A0A0C0]">
              Click the play button inside the Spotify player below. You can minimize this window at any time and the music will continue playing seamlessly while you browse the guide.
            </p>
          </div>

          <!-- Embedded Spotify Player Iframe Container (Persistent across open/close) -->
          <div class="border-2 border-[#1DB954] bg-black p-1 rounded-xs shadow-inner">
            <iframe
              ref="spotifyIframeRef"
              style="border-radius: 4px"
              :src="computedSpotifyEmbedUrl"
              width="100%"
              height="152"
              frameBorder="0"
              allowfullscreen
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>

          <!-- External Launch & Options -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 border-t border-[#333366]">
            <a
              :href="playlistUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="w-full sm:w-auto px-4 py-2 bg-[#1DB954] text-[#000033] hover:bg-[#FFFFFF] font-black text-center tracking-wider transition-all cursor-pointer shadow-[0_0_10px_rgba(29,185,84,0.6)]"
            >
              [ OPEN IN SPOTIFY APP / WEB ]
            </a>

            <button
              type="button"
              class="w-full sm:w-auto px-4 py-2 bg-[#000044] border border-[#333366] text-[#8888AA] hover:text-[#FFFFFF] hover:border-[#8888AA] font-bold cursor-pointer transition-all"
              @click="minimize"
            >
              [ MINIMIZE & KEEP PLAYING ]
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- PERSISTENT FLOATING MINI-DOCK (WHEN MINIMIZED BUT AUDIO LOADED) -->
    <div
      v-show="!isOpen && isDockVisible"
      class="fixed bottom-3 right-3 z-40 bg-[#000033]/95 backdrop-blur-xs border-2 border-[#1DB954] text-[#E0E0E0] p-2.5 rounded-xs shadow-[0_0_16px_rgba(29,185,84,0.5)] font-mono text-xs select-none max-w-xs flex flex-col space-y-2 transition-all duration-200"
    >
      <div class="flex items-center justify-between space-x-2 border-b border-[#1DB954]/40 pb-1.5">
        <div class="flex items-center space-x-1.5 truncate">
          <div class="flex items-end space-x-0.5 h-3 text-[#1DB954]">
            <span class="w-0.5 bg-current animate-pulse h-2"></span>
            <span class="w-0.5 bg-current animate-pulse h-3"></span>
            <span class="w-0.5 bg-current animate-pulse h-1.5"></span>
          </div>
          <span class="text-[10px] font-black text-[#1DB954] uppercase tracking-wider truncate">
            SPOTIFY HEADEND ACTIVE
          </span>
        </div>
        <div class="flex items-center space-x-1 shrink-0">
          <button
            type="button"
            class="text-[10px] bg-[#000066] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-1.5 py-0.2 font-bold cursor-pointer transition-colors"
            @click="expand"
            title="Expand Spotify Player"
          >
            [ EXPAND ]
          </button>
          <button
            type="button"
            class="text-[10px] text-[#8888AA] hover:text-[#FFFFFF] px-1 font-bold cursor-pointer"
            @click="hideDock"
            title="Hide dock widget (audio continues in background)"
          >
            [ X ]
          </button>
        </div>
      </div>

      <div class="text-[10px] text-[#A0A0C0] truncate">
        PLAYLIST: <span class="text-[#FFFF00] font-bold">"{{ playlistTitle }}"</span>
        <span v-if="playlistAuthor"> by <span class="text-[#00FFFF] font-bold">{{ playlistAuthor }}</span></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchSpotifyMetadata } from '../api/client'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    customPlaylistUrl?: string
  }>(),
  {
    isOpen: false,
    customPlaylistUrl: '',
  }
)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'open'): void
}>()

const isDockVisible = ref(true)
const playlistTitle = ref('OpenPrevue')
const playlistAuthor = ref('upioneer')

const DEFAULT_PLAYLIST = 'https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f'

const playlistUrl = computed(() => props.customPlaylistUrl || DEFAULT_PLAYLIST)

const computedSpotifyEmbedUrl = computed(() => {
  const url = playlistUrl.value
  const match = url.match(/playlist\/([a-zA-Z0-9]+)/)
  const playlistId = match ? match[1] : '3jiPmIT4RugR8TPhli5Obk'
  return `https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator&theme=0`
})

async function loadMetadata() {
  try {
    const meta = await fetchSpotifyMetadata(playlistUrl.value)
    if (meta.title) {
      playlistTitle.value = meta.title
    }
    if (meta.author_name) {
      playlistAuthor.value = meta.author_name
    }
  } catch (err) {
    console.debug('Failed resolving dynamic Spotify metadata:', err)
  }
}

watch(() => playlistUrl.value, () => {
  loadMetadata()
})

onMounted(() => {
  loadMetadata()
})

function minimize() {
  isDockVisible.value = true
  emit('close')
}

function expand() {
  emit('open')
}

function hideDock() {
  isDockVisible.value = false
}
</script>
