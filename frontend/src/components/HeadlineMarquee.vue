<template>
  <div
    ref="containerRef"
    class="w-full overflow-hidden whitespace-nowrap relative cursor-pointer select-none group/headline"
    :title="title"
    @click="$emit('click')"
  >
    <!-- Invisible measuring element for accurate title width calculation -->
    <span
      ref="measureRef"
      class="invisible absolute pointer-events-none whitespace-nowrap font-black"
      :class="customClasses"
      aria-hidden="true"
    >
      {{ title }}
    </span>

    <!-- Continuous One-Direction Scrolling Marquee with Repeating Title -->
    <div
      v-if="isOverflowing"
      class="inline-flex items-center whitespace-nowrap animate-headline-marquee will-change-transform"
      :style="marqueeStyle"
    >
      <!-- Block 1 (Reference Block) -->
      <span ref="firstBlockRef" class="inline-flex items-center shrink-0">
        <span
          class="inline-block font-black hover:underline transition-colors shrink-0"
          :class="[
            customClasses,
            hasTicket ? 'text-[#00FF00]' : 'text-[#FFFF00]'
          ]"
        >
          {{ title }}
        </span>
        <span class="inline-block mx-5 text-[#00FFFF] font-black shrink-0 select-none opacity-80">
          //
        </span>
      </span>

      <!-- Block 2 (Repeat) -->
      <span class="inline-flex items-center shrink-0" aria-hidden="true">
        <span
          class="inline-block font-black hover:underline transition-colors shrink-0"
          :class="[
            customClasses,
            hasTicket ? 'text-[#00FF00]' : 'text-[#FFFF00]'
          ]"
        >
          {{ title }}
        </span>
        <span class="inline-block mx-5 text-[#00FFFF] font-black shrink-0 select-none opacity-80">
          //
        </span>
      </span>

      <!-- Block 3 (Buffer for Wide Grid Cells) -->
      <span class="inline-flex items-center shrink-0" aria-hidden="true">
        <span
          class="inline-block font-black hover:underline transition-colors shrink-0"
          :class="[
            customClasses,
            hasTicket ? 'text-[#00FF00]' : 'text-[#FFFF00]'
          ]"
        >
          {{ title }}
        </span>
        <span class="inline-block mx-5 text-[#00FFFF] font-black shrink-0 select-none opacity-80">
          //
        </span>
      </span>
    </div>

    <!-- Static Truncated Fallback for Short Non-Overflowing Titles -->
    <span
      v-else
      class="truncate block font-black hover:underline transition-colors"
      :class="[
        customClasses,
        hasTicket ? 'text-[#00FF00]' : 'text-[#FFFF00]'
      ]"
    >
      {{ title }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    hasTicket?: boolean
    customClasses?: string
  }>(),
  {
    hasTicket: false,
    customClasses: '',
  }
)

defineEmits<{
  (e: 'click'): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const measureRef = ref<HTMLElement | null>(null)
const firstBlockRef = ref<HTMLElement | null>(null)
const isOverflowing = ref(false)
const repeatDistance = ref(0)
const marqueeDuration = ref(8)

let resizeObserver: ResizeObserver | null = null

const marqueeStyle = computed(() => {
  return {
    '--repeat-distance': `${repeatDistance.value}px`,
    '--marquee-duration': `${marqueeDuration.value}s`,
  }
})

function checkOverflow() {
  if (!containerRef.value || !measureRef.value) return
  const containerWidth = containerRef.value.clientWidth
  const textWidth = measureRef.value.offsetWidth

  if (textWidth > containerWidth + 4) {
    isOverflowing.value = true
    nextTick(() => {
      if (firstBlockRef.value) {
        const dist = firstBlockRef.value.offsetWidth
        repeatDistance.value = dist
        // Balanced reading speed: ~30px per second plus 2.2s pause at start
        marqueeDuration.value = Math.max(6, Math.round(dist / 30) + 2)
      }
    })
  } else {
    isOverflowing.value = false
    repeatDistance.value = 0
  }
}

watch(
  () => props.title,
  async () => {
    await nextTick()
    checkOverflow()
  }
)

onMounted(async () => {
  await nextTick()
  checkOverflow()

  if (containerRef.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      checkOverflow()
    })
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})
</script>

<style scoped>
@keyframes prevue-headline-marquee {
  0%, 18% {
    transform: translateX(0);
  }
  98%, 100% {
    transform: translateX(calc(-1 * var(--repeat-distance)));
  }
}

.animate-headline-marquee {
  animation: prevue-headline-marquee var(--marquee-duration) cubic-bezier(0.42, 0, 0.58, 1) infinite;
  will-change: transform;
}

.group\/headline:hover .animate-headline-marquee {
  animation-play-state: paused;
}
</style>
