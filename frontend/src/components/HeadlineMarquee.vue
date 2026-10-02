<template>
  <div
    ref="containerRef"
    class="w-full overflow-hidden whitespace-nowrap relative cursor-pointer select-none group/headline"
    :title="title"
    @click="$emit('click')"
  >
    <span
      ref="textRef"
      class="inline-block font-black hover:underline transition-colors"
      :class="[
        customClasses,
        hasTicket ? 'text-[#00FF00]' : 'text-[#FFFF00]',
        isOverflowing ? 'animate-headline-marquee' : 'truncate block'
      ]"
      :style="isOverflowing ? marqueeStyle : undefined"
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
const textRef = ref<HTMLElement | null>(null)
const isOverflowing = ref(false)
const overflowDistance = ref(0)
const marqueeDuration = ref(6)

let resizeObserver: ResizeObserver | null = null

const marqueeStyle = computed(() => {
  return {
    '--overflow-distance': `${overflowDistance.value}px`,
    '--marquee-duration': `${marqueeDuration.value}s`,
  }
})

function checkOverflow() {
  if (!containerRef.value || !textRef.value) return
  const containerWidth = containerRef.value.clientWidth
  const textWidth = textRef.value.scrollWidth

  if (textWidth > containerWidth + 4) {
    isOverflowing.value = true
    const diff = textWidth - containerWidth
    overflowDistance.value = diff
    // Smooth reading velocity: ~28px/second plus reading pauses
    marqueeDuration.value = Math.max(5, Math.round(diff / 28) + 3)
  } else {
    isOverflowing.value = false
    overflowDistance.value = 0
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
  0%, 20% {
    transform: translateX(0);
  }
  80%, 100% {
    transform: translateX(calc(-1 * var(--overflow-distance)));
  }
}

.animate-headline-marquee {
  animation: prevue-headline-marquee var(--marquee-duration) ease-in-out infinite alternate;
  will-change: transform;
}

.group\/headline:hover .animate-headline-marquee {
  animation-play-state: paused;
}
</style>
