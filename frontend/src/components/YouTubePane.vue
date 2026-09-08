<template>
  <div
    class="w-full h-full bg-[#000018] flex flex-col justify-between overflow-hidden select-none font-mono relative"
    :class="isUltrawide ? 'border-b-0' : 'border-b-2 border-[#FFFF00]'"
  >
    <!-- CRT TV Aspect-Ratio Centered Stage Container -->
    <div class="flex-1 w-full min-h-0 flex items-center justify-center overflow-hidden relative bg-[#000011]">
      <!-- Vintage TV NTSC Pillarbox Side Bezels (Active during 4:3 or 16:9 framing on wide screens) -->
      <div
        v-if="aspectRatio === '4:3' || aspectRatio === '16:9'"
        class="absolute inset-y-0 left-0 w-10 sm:w-16 bg-gradient-to-r from-black via-[#000022] to-transparent pointer-events-none flex flex-col justify-between py-2 px-2 z-10 opacity-70"
      >
        <span class="text-[9px] sm:text-[10px] text-[#00FFFF] font-black uppercase tracking-widest rotate-90 origin-bottom-left whitespace-nowrap">
          {{ aspectRatio === '4:3' ? 'NTSC 4:3' : '16:9 WIDE' }}
        </span>
        <span class="text-[8px] sm:text-[9px] text-[#FFFF00] font-mono">CH-03</span>
      </div>

      <div
        v-if="aspectRatio === '4:3' || aspectRatio === '16:9'"
        class="absolute inset-y-0 right-0 w-10 sm:w-16 bg-gradient-to-l from-black via-[#000022] to-transparent pointer-events-none flex flex-col justify-between py-2 px-2 z-10 opacity-70 items-end"
      >
        <span class="text-[9px] sm:text-[10px] text-[#00FF00] font-black uppercase tracking-widest -rotate-90 origin-bottom-right whitespace-nowrap">
          {{ audioMode === 'audio' ? 'LIVE AUDIO' : 'MUTED RF' }}
        </span>
        <span class="text-[8px] sm:text-[9px] text-[#00FFFF] font-mono">PREVUE</span>
      </div>

      <!-- Video Player Frame with Sized Aspect Box -->
      <div
        class="h-full relative overflow-hidden transition-all duration-300"
        :class="frameAspectClass"
      >
        <div :id="playerId" class="w-full h-full pointer-events-auto"></div>
      </div>
    </div>

    <!-- Retro Broadcast Stream Telemetry Footer (Matches SpotlightPane aesthetic) -->
    <div class="h-7 sm:h-8 w-full bg-[#000022]/95 backdrop-blur-xs border-t border-[#FF0000]/40 flex items-center justify-between px-3 text-xs sm:text-sm font-mono text-[#E0E0E0] shrink-0 select-none shadow-md z-20">
      <!-- Left: YouTube Broadcast Status -->
      <div class="flex items-center space-x-2 shrink-0">
        <div class="flex items-center space-x-1.5">
          <span class="w-2.5 h-2.5 bg-[#FF0000] inline-block animate-ping rounded-full"></span>
          <span class="font-black text-xs sm:text-sm tracking-wider text-[#FF0000]">
            YOUTUBE STREAM
          </span>
        </div>
      </div>

      <!-- Center: Marquee Stream Telemetry -->
      <div class="flex-1 overflow-hidden ml-4 mr-2 text-center">
        <div class="inline-block whitespace-nowrap text-xs text-[#FFFF00] font-bold tracking-widest animate-marquee uppercase">
          {{ streamTelemetryText }}
        </div>
      </div>

      <!-- Right: Channel Skipper & Audio Status Badge -->
      <div class="shrink-0 flex items-center space-x-2">
        <button
          v-if="parsedResource.type === 'playlist'"
          type="button"
          class="text-[10px] sm:text-xs font-black uppercase px-2 py-0.5 border cursor-pointer transition-colors bg-[#000044] text-[#FFFF00] border-[#FFFF00] hover:bg-[#FFFF00] hover:text-[#000033]"
          @click="skipNextClip"
          title="Skip to next playlist clip"
        >
          [ NEXT CLIP &gt;&gt; ]
        </button>

        <button
          type="button"
          class="text-[10px] sm:text-xs font-black uppercase px-2 py-0.5 border cursor-pointer transition-colors"
          :class="audioMode === 'audio' ? 'bg-[#00FF00] text-[#000033] border-[#FFFF00]' : 'bg-[#000044] text-[#00FFFF] border-[#00FFFF]'"
          @click="toggleAudio"
          :title="audioMode === 'audio' ? 'Mute YouTube Audio' : 'Enable YouTube Audio'"
        >
          [ {{ audioMode === 'audio' ? 'AUDIO ON' : 'AUDIO MUTED' }} ]
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { audioSynth } from '../services/audioSynth'

const props = withDefaults(
  defineProps<{
    sourceUrl: string
    audioMode?: 'mute' | 'audio' | string
    aspectRatio?: 'auto' | '4:3' | '16:9' | 'stretch' | string
    isUltrawide?: boolean
    shuffleEnabled?: string | boolean
  }>(),
  {
    audioMode: 'mute',
    aspectRatio: '4:3',
    isUltrawide: false,
    shuffleEnabled: false,
  }
)

const emit = defineEmits<{
  (e: 'error', code: number): void
  (e: 'update:audioMode', mode: string): void
}>()

const playerId = `yt-player-${Math.random().toString(36).substring(2, 9)}`
let playerInstance: any = null
const currentVideoTitle = ref<string>('')
const isPlaying = ref(false)

const isShuffleOn = computed(() => {
  return props.shuffleEnabled === true || props.shuffleEnabled === '1' || props.shuffleEnabled === 'true'
})

// Determine aspect ratio class for video container
const frameAspectClass = computed(() => {
  switch (props.aspectRatio) {
    case '4:3':
      return 'aspect-[4/3] max-h-full max-w-full mx-auto shadow-2xl border-x-2 border-[#222255]'
    case '16:9':
      return 'aspect-video max-h-full max-w-full mx-auto shadow-2xl border-x-2 border-[#222255]'
    case 'stretch':
      return 'w-full h-full'
    case 'auto':
    default:
      return 'w-full h-full flex items-center justify-center'
  }
})

// Parse YouTube resource from input
const parsedResource = computed(() => {
  const clean = (props.sourceUrl || '').trim()
  if (!clean) return { type: 'unknown', id: '' }

  const listMatch = clean.match(/[?&]list=([a-zA-Z0-9_-]+)/)
  if (listMatch) return { type: 'playlist', id: listMatch[1] }

  if (/^(PL|UU|FL|RD|OLAK)[a-zA-Z0-9_-]+$/i.test(clean)) {
    return { type: 'playlist', id: clean }
  }

  const vidMatch = clean.match(/(?:v=|\/embed\/|\/shorts\/|\/live\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  if (vidMatch) return { type: 'video', id: vidMatch[1] }

  if (/^[a-zA-Z0-9_-]{11}$/.test(clean)) {
    return { type: 'video', id: clean }
  }

  return { type: 'unknown', id: clean }
})

const streamTelemetryText = computed(() => {
  const title = currentVideoTitle.value ? `"${currentVideoTitle.value.toUpperCase()}"` : 'ACTIVE TRANSMISSION'
  const modeText = props.audioMode === 'audio' ? 'LIVE STEREO AUDIO' : 'MUTED (BACKGROUND RETRO MUSIC ENGAGED)'
  return `ON AIR // VINTAGE RETRO REEL // ${title} // ${modeText} // OPENPREVUE RETRO CABLE`
})

function toggleAudio() {
  const nextMode = props.audioMode === 'audio' ? 'mute' : 'audio'
  emit('update:audioMode', nextMode)
  if (playerInstance) {
    if (nextMode === 'mute') {
      playerInstance.mute()
    } else {
      playerInstance.unMute()
    }
  }
}

function skipNextClip() {
  if (playerInstance && typeof playerInstance.nextVideo === 'function') {
    playerInstance.nextVideo()
  }
}

// Load YouTube IFrame API script dynamically
function initYouTubeApi(): Promise<void> {
  return new Promise((resolve) => {
    if ((window as any).YT && (window as any).YT.Player) {
      resolve()
      return
    }

    const prevReady = (window as any).onYouTubeIframeAPIReady
    ;(window as any).onYouTubeIframeAPIReady = () => {
      if (prevReady) prevReady()
      resolve()
    }

    if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
      const tag = document.createElement('script')
      tag.src = 'https://www.youtube.com/iframe_api'
      document.head.appendChild(tag)
    }
  })
}

async function mountPlayer() {
  if (parsedResource.value.type === 'unknown' || !parsedResource.value.id) {
    emit('error', 2)
    return
  }

  await initYouTubeApi()

  if (playerInstance) {
    try {
      playerInstance.destroy()
    } catch {
      // Ignore destroy failure
    }
    playerInstance = null
  }

  const isPlaylist = parsedResource.value.type === 'playlist'
  const isMuted = props.audioMode === 'mute'

  const playerVars: any = {
    autoplay: 1,
    mute: isMuted ? 1 : 0,
    controls: 0,
    modestbranding: 1,
    rel: 0,
    fs: 0,
    iv_load_policy: 3,
    disablekb: 1,
    playsinline: 1,
    enablejsapi: 1,
    origin: window.location.origin,
  }

  if (isPlaylist) {
    playerVars.listType = 'playlist'
    playerVars.list = parsedResource.value.id
    playerVars.loop = 1
  } else {
    playerVars.playlist = parsedResource.value.id
    playerVars.loop = 1
  }

  playerInstance = new (window as any).YT.Player(playerId, {
    height: '100%',
    width: '100%',
    videoId: isPlaylist ? undefined : parsedResource.value.id,
    playerVars,
    events: {
      onReady: (e: any) => {
        if (isMuted) {
          e.target.mute()
        } else {
          e.target.unMute()
        }
        if (isPlaylist && isShuffleOn.value && typeof e.target.setShuffle === 'function') {
          e.target.setShuffle(true)
        }
        e.target.playVideo()
        updateTitle()
      },
      onStateChange: (e: any) => {
        // e.data: -1 unstarted, 0 ended, 1 playing, 2 paused, 3 buffering, 5 cued
        if (e.data === 1) {
          isPlaying.value = true
          updateTitle()
        } else if (e.data === 0) {
          // Continuous loop
          if (isPlaylist) {
            e.target.nextVideo()
          } else {
            e.target.playVideo()
          }
        }
      },
      onError: (e: any) => {
        // Error codes: 2 (invalid param), 5 (HTML5 error), 100 (not found), 101/150 (not allowed to embed)
        console.warn('YouTube Player error code:', e.data)
        emit('error', e.data)
      },
    },
  })
}

function updateTitle() {
  if (playerInstance && typeof playerInstance.getVideoData === 'function') {
    const data = playerInstance.getVideoData()
    if (data?.title) {
      currentVideoTitle.value = data.title
    }
  }
}

// Pause video during active EAS emergency sirens
watch(() => audioSynth.isEASSirenPlaying.value, (isSiren) => {
  if (!playerInstance) return
  if (isSiren) {
    playerInstance.pauseVideo()
  } else {
    playerInstance.playVideo()
  }
})

// Sync audioMode prop changes
watch(() => props.audioMode, (mode) => {
  if (!playerInstance) return
  if (mode === 'mute') {
    playerInstance.mute()
  } else {
    playerInstance.unMute()
  }
})

// Sync shuffleEnabled prop changes
watch(isShuffleOn, (val) => {
  if (playerInstance && parsedResource.value.type === 'playlist' && typeof playerInstance.setShuffle === 'function') {
    playerInstance.setShuffle(val)
  }
})

// Remount player on source URL change
watch(() => props.sourceUrl, () => {
  mountPlayer()
})

onMounted(() => {
  mountPlayer()
})

onUnmounted(() => {
  if (playerInstance) {
    try {
      playerInstance.destroy()
    } catch {
      // Ignore cleanup error
    }
    playerInstance = null
  }
})
</script>
