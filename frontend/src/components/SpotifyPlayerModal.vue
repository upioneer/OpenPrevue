<template>
  <div>
    <!-- FULL MODAL OVERLAY (EXPANDED MODE) -->
    <div
      v-show="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xs p-3 sm:p-4 select-none font-mono transition-opacity duration-200"
      @click.self="minimize"
    >
      <div
        class="w-full max-w-xl bg-gradient-to-b from-[#000088] via-[#000055] to-[#000022] border-2 border-[#1DB954] rounded-xs shadow-[0_0_30px_rgba(29,185,84,0.7)] overflow-hidden flex flex-col max-h-[90vh]"
      >
        <!-- Top Title Bar -->
        <div class="bg-[#0000AA] border-b-2 border-[#1DB954] px-3 sm:px-4 py-2 flex items-center justify-between shrink-0">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 bg-[#1DB954] inline-block animate-pulse"></span>
            <span class="text-xs sm:text-sm font-black text-[#1DB954] tracking-widest uppercase">
              [ SPOTIFY HEADEND AUDIO PLAYER ]
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <button
              type="button"
              class="bg-[#1DB954] hover:bg-[#FFFFFF] text-[#000033] px-2.5 py-0.5 text-xs font-black uppercase cursor-pointer transition-all shadow-[0_0_8px_rgba(29,185,84,0.6)]"
              @click="playAndMinimize"
              title="Start audio playback and return to the channel guide"
            >
              [ PLAY & MINIMIZE ]
            </button>
            <button
              type="button"
              class="text-xs text-[#00FFFF] hover:text-[#FFFFFF] border border-[#00FFFF] px-2 py-0.5 font-bold cursor-pointer transition-colors"
              @click="minimize"
              title="Close modal without modifying playback"
            >
              [ X ]
            </button>
          </div>
        </div>

        <!-- Body Content (High Contrast Custom Scrollbar) -->
        <div class="p-3 sm:p-4 space-y-3 text-xs overflow-y-auto high-contrast-scrollbar flex-1">
          <div class="bg-[#000033] border border-[#333366] p-3 text-[#E0E0E0] leading-relaxed space-y-1.5">
            <div class="text-[#FFFF00] font-black uppercase flex items-center justify-between text-xs sm:text-sm">
              <span>PLAYLIST: "{{ playlistTitle }}" {{ playlistAuthor ? 'BY ' + playlistAuthor.toUpperCase() : '' }}</span>
              <span class="text-[#1DB954] text-xs">[ LIVE SPOTIFY SYNC ]</span>
            </div>
            <p class="text-xs text-[#A0A0C0]">
              Click the play button inside the Spotify player below or click <span class="text-[#1DB954] font-bold">[ PLAY & MINIMIZE ]</span>. Audio continues playing seamlessly in the background while you navigate the Prevue channel guide.
            </p>
          </div>

          <!-- Embedded Spotify Player Iframe Container (High-Contrast Border & Glow) -->
          <div class="border-2 border-[#1DB954] bg-black p-1 rounded-xs shadow-[0_0_14px_rgba(29,185,84,0.3)]">
            <iframe
              ref="spotifyIframeRef"
              style="border-radius: 4px"
              :src="computedSpotifyEmbedUrl"
              width="100%"
              height="232"
              frameBorder="0"
              allowfullscreen
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>

          <!-- Doubled Action Controls -->
          <div class="flex flex-col sm:flex-row items-center justify-between gap-2 pt-2 border-t border-[#333366]">
            <!-- Primary Action: Play & Minimize -->
            <button
              type="button"
              class="w-full sm:w-auto px-4 py-2 bg-[#1DB954] hover:bg-[#FFFFFF] text-[#000033] font-black text-center tracking-wider text-xs uppercase cursor-pointer transition-all shadow-[0_0_12px_rgba(29,185,84,0.7)]"
              @click="playAndMinimize"
              title="Ensure background audio is playing and return to the guide"
            >
              [ PLAY & MINIMIZE TO GUIDE ]
            </button>

            <!-- Secondary Actions -->
            <div class="flex items-center space-x-2 w-full sm:w-auto">
              <button
                type="button"
                class="flex-1 sm:flex-initial px-3 py-2 bg-[#000044] border border-[#00FFFF] text-[#00FFFF] hover:bg-[#000088] font-bold text-center tracking-wider text-xs uppercase cursor-pointer transition-all"
                @click="minimize"
                title="Return to the channel guide"
              >
                [ MINIMIZE ONLY ]
              </button>

              <a
                :href="playlistUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="flex-1 sm:flex-initial px-3 py-2 bg-[#000022] border border-[#333366] text-[#8888AA] hover:text-[#FFFFFF] hover:border-[#8888AA] font-bold text-center tracking-wider text-xs uppercase transition-all"
              >
                [ OPEN APP ]
              </a>
            </div>
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
import { audioSynth } from '../services/audioSynth'

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
const spotifyIframeRef = ref<HTMLIFrameElement | null>(null)

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

function playAndMinimize() {
  // Ensure audio atmosphere is running
  if (!audioSynth.isAudioActive.value) {
    audioSynth.startTurnkeyAudio()
  }

  // Attempt postMessage to Spotify Embed iframe
  try {
    if (spotifyIframeRef.value && spotifyIframeRef.value.contentWindow) {
      spotifyIframeRef.value.contentWindow.postMessage({ command: 'play' }, '*')
      spotifyIframeRef.value.contentWindow.postMessage({ command: 'toggle' }, '*')
    }
  } catch {
    // Cross-origin safe
  }

  minimize()
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

<style scoped>
.high-contrast-scrollbar {
  scrollbar-color: #FFFF00 #000033;
  scrollbar-width: thin;
}

.high-contrast-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.high-contrast-scrollbar::-webkit-scrollbar-track {
  background: #000022;
  border: 1px solid #333366;
}

.high-contrast-scrollbar::-webkit-scrollbar-thumb {
  background: #FFFF00;
  border: 1px solid #000000;
  border-radius: 2px;
}

.high-contrast-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #00FFFF;
}
</style>
