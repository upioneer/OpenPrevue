<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xs p-4 select-none font-mono"
  >
    <div
      class="w-full max-w-3xl bg-gradient-to-b from-[#000088] via-[#000044] to-[#000022] border-2 border-[#00FF00] rounded-xs shadow-[0_0_28px_rgba(0,255,0,0.6)] overflow-hidden max-h-[92vh] flex flex-col"
    >
      <!-- Title Bar -->
      <div class="bg-[#0000AA] border-b-2 border-[#00FF00] px-4 py-2.5 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 bg-[#00FF00] inline-block animate-pulse"></span>
          <span class="text-sm font-black text-[#00FF00] tracking-widest uppercase">
            [ OPENPREVUE v{{ releaseData.version }} // UPDATE RELEASE NOTES ]
          </span>
        </div>
        <span class="text-xs text-[#00FFFF] font-bold tracking-wider uppercase">SYSTEM UPDATED</span>
      </div>

      <!-- Scrollable Body -->
      <div class="p-4 sm:p-6 space-y-4 text-xs overflow-y-auto">
        <!-- Banner -->
        <div class="bg-[#000033] border border-[#00FF00]/60 p-3 text-[#E0E0E0] leading-relaxed">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[#00FF00] font-black uppercase text-xs">
              SYSTEM UPGRADE COMPLETE: OPENPREVUE v{{ releaseData.version }}
            </span>
            <span class="text-[10px] bg-[#003300] text-[#00FF00] border border-[#00FF00] px-1.5 py-0.5 font-bold uppercase">
              ONLINE &amp; ACTIVE
            </span>
          </div>
          <div class="text-[#FFFF00] font-bold text-xs uppercase mb-1">
            {{ releaseData.title }}
          </div>
          <p class="text-[11px] text-[#A0A0C0]">
            Your OpenPrevue headend instance has been updated. Review the key features, enhancements, and operational improvements included in this build:
          </p>
        </div>

        <!-- Release Highlights Checklist -->
        <div class="bg-[#000022] p-4 border border-[#333366] space-y-2.5">
          <div class="text-xs font-bold text-[#00FFFF] uppercase tracking-wider border-b border-[#333366] pb-1.5">
            // RELEASE HIGHLIGHTS &amp; ARCHITECTURAL IMPROVEMENTS
          </div>
          <ul class="space-y-2 text-[11px] text-[#C0C0E0]">
            <li
              v-for="(item, idx) in releaseData.highlights"
              :key="idx"
              class="flex items-start space-x-2.5"
            >
              <span class="text-[#00FF00] font-black shrink-0">*</span>
              <span class="leading-relaxed">{{ item }}</span>
            </li>
          </ul>
        </div>

        <!-- Deep Link to Documentation -->
        <div class="bg-[#000022] p-3.5 border border-[#00FFFF] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="space-y-1">
            <span class="text-xs font-bold text-[#00FFFF] uppercase block">
              DETAILED CHANGELOG &amp; SCREENSHOT SHOWCASE
            </span>
            <p class="text-[11px] text-[#A0A0C0]">
              View complete version history, architectural diagrams, proof logs, and multi-screen screenshot showcases in Settings Tab 11.
            </p>
          </div>
          <button
            type="button"
            class="px-3 py-1.5 bg-[#000066] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] text-xs font-bold uppercase cursor-pointer shrink-0 transition-colors"
            @click="handleNavigateToGuide"
          >
            [ VIEW DOCUMENTATION ]
          </button>
        </div>

        <!-- Footer Dismissal Controls -->
        <div class="pt-3 border-t border-[#00FF00]/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <!-- Never Show Again Checkbox -->
          <label class="flex items-center space-x-2 cursor-pointer text-xs text-[#E0E0E0] hover:text-[#00FF00] transition-colors select-none">
            <input
              v-model="neverShowAgain"
              type="checkbox"
              class="w-4 h-4 accent-[#00FF00] cursor-pointer"
            />
            <span class="font-bold uppercase tracking-wider">
              Do Not Show Release Notes on Future Updates
            </span>
          </label>

          <!-- Dismiss Button -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              type="button"
              class="px-5 py-2 bg-[#00FF00] text-[#000033] hover:bg-[#FFFFFF] border-2 border-[#00FF00] font-black uppercase cursor-pointer shadow-[0_0_12px_rgba(0,255,0,0.8)] transition-all"
              @click="handleDismiss"
            >
              [ CONTINUE BROADCAST ]
            </button>
          </div>
        </div>

        <!-- Preferences Note -->
        <div class="text-[10px] text-[#8888AA] text-center pt-1">
          * You can re-enable update notifications or review past changelogs in <strong>Settings &gt; Tab 11 (User Onboarding &amp; Deployment Guide)</strong>.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getReleaseNotes } from '../services/releaseNotes'

const props = defineProps<{
  isOpen: boolean
  version?: string
}>()

const emit = defineEmits<{
  (e: 'close', neverShowAgain: boolean, version: string): void
}>()

const router = useRouter()
const neverShowAgain = ref(false)

const releaseData = computed(() => {
  return getReleaseNotes(props.version)
})

function handleDismiss() {
  emit('close', neverShowAgain.value, releaseData.value.version)
}

function handleNavigateToGuide() {
  emit('close', neverShowAgain.value, releaseData.value.version)
  router.push({ path: '/settings', query: { tab: 'guide' } })
}
</script>
