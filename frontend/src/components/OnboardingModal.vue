<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-xs p-4 select-none font-mono"
  >
    <div
      class="w-full max-w-3xl bg-gradient-to-b from-[#000088] via-[#000044] to-[#000022] border-2 border-[#FFFF00] rounded-xs shadow-[0_0_28px_rgba(255,255,0,0.6)] overflow-hidden max-h-[92vh] flex flex-col"
    >
      <!-- Title Bar -->
      <div class="bg-[#0000AA] border-b-2 border-[#FFFF00] px-4 py-2.5 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2">
          <span class="w-3 h-3 bg-[#00FF00] inline-block animate-pulse"></span>
          <span class="text-sm font-black text-[#FFFF00] tracking-widest uppercase">
            [ OPENPREVUE // OPERATOR QUICK START ]
          </span>
        </div>
        <span class="text-xs text-[#00FFFF] font-bold tracking-wider uppercase">SYSTEM ORIENTATION</span>
      </div>

      <!-- Scrollable Content Body -->
      <div class="p-4 sm:p-6 space-y-4 text-xs overflow-y-auto">
        <!-- Intro Banner -->
        <div class="bg-[#000033] border border-[#00FFFF]/60 p-3 text-[#E0E0E0] leading-relaxed">
          <span class="text-[#FFFF00] font-black uppercase block mb-1">
            WELCOME TO YOUR PERSONALIZED 1990S CABLE GUIDE
          </span>
          OpenPrevue transforms local live events, concert tours, sports matches, and travel wishlists into an authentic vintage broadcast. Here is where to find key controls and unlock advanced features:
        </div>

        <!-- Quick Landmark Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <!-- 1. Settings Control Center -->
          <div class="bg-[#000022] p-3 border border-[#333366] space-y-1.5 hover:border-[#00FFFF] transition-colors">
            <div class="flex items-center justify-between">
              <span class="bg-[#000066] text-[#00FFFF] text-[10px] font-black px-1.5 py-0.5 border border-[#00FFFF]">
                TOP RIGHT [ SETTINGS ]
              </span>
              <span class="text-[10px] text-[#8888AA] font-bold">11 TABS</span>
            </div>
            <div class="text-xs font-bold text-[#FFFF00] uppercase">
              1. System Settings Control Center
            </div>
            <p class="text-[11px] text-[#C0C0E0] leading-normal">
              Click <strong>[ SETTINGS ]</strong> in the top header bar to configure discovery radius, 4:3 vs 16:9 CRT styling, live YouTube comp reels, audio volumes, and real-time system health telemetry.
            </p>
          </div>

          <!-- 2. Curated Spotify Radio -->
          <div class="bg-[#000022] p-3 border border-[#333366] space-y-1.5 hover:border-[#00FF00] transition-colors">
            <div class="flex items-center justify-between">
              <span class="bg-[#003300] text-[#00FF00] text-[10px] font-black px-1.5 py-0.5 border border-[#00FF00]">
                TOP RIGHT [ SPOTIFY ]
              </span>
              <span class="text-[10px] text-[#00FF00] font-bold">LIVE AUDIO</span>
            </div>
            <div class="text-xs font-bold text-[#00FF00] uppercase">
              2. Curated 1990s Synth &amp; Jazz Radio
            </div>
            <p class="text-[11px] text-[#C0C0E0] leading-normal">
              Click <strong>[ SPOTIFY ]</strong> or the lower-right ticker to open the built-in player. Enjoy authentic 1990s weather channel jazz, override with your personal playlist URL, and tune tape hiss static.
            </p>
          </div>

          <!-- 3. Where to Add Events -->
          <div class="bg-[#000022] p-3 border border-[#333366] space-y-1.5 hover:border-[#FFFF00] transition-colors">
            <div class="flex items-center justify-between">
              <span class="bg-[#332200] text-[#FFFF00] text-[10px] font-black px-1.5 py-0.5 border border-[#FFFF00]">
                SETTINGS TAB 1 &amp; TAB 5
              </span>
              <span class="text-[10px] text-[#FFFF00] font-bold">EVENT INGEST</span>
            </div>
            <div class="text-xs font-bold text-[#FFFF00] uppercase">
              3. Where to Add Events &amp; Wishlists
            </div>
            <p class="text-[11px] text-[#C0C0E0] leading-normal">
              Go to <strong>Settings &gt; Tab 5</strong> to paste public <strong>TripAdvisor</strong> or <strong>Viator</strong> wishlist URLs and iCal feeds. Or go to <strong>Tab 1</strong> to register custom venues and manual listings.
            </p>
          </div>

          <!-- 4. Opt-in Local AI Support -->
          <div class="bg-[#000022] p-3 border border-[#333366] space-y-1.5 hover:border-[#FF88FF] transition-colors">
            <div class="flex items-center justify-between">
              <span class="bg-[#2E0854] text-[#FF88FF] text-[10px] font-black px-1.5 py-0.5 border border-[#CC44FF]">
                SETTINGS TAB 5 [ AI ]
              </span>
              <span class="text-[10px] text-[#FF88FF] font-bold">OPT-IN</span>
            </div>
            <div class="text-xs font-bold text-[#FF88FF] uppercase">
              4. Opt-In Local AI Flyer Ingestion
            </div>
            <p class="text-[11px] text-[#C0C0E0] leading-normal">
              Connect a self-hosted <strong>Ollama</strong> instance in Tab 5. OpenPrevue uses local LLMs to parse messy concert flyers, emails, and unstructured text directly into broadcast listings with zero cloud leaks.
            </p>
          </div>
        </div>

        <!-- 5. Full Onboarding Tour Callout -->
        <div class="bg-[#000022] p-3.5 border border-[#00FFFF] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="bg-[#000066] text-[#00FFFF] text-[10px] font-black px-1.5 py-0.5 border border-[#00FFFF]">
                SETTINGS TAB 11
              </span>
              <span class="text-xs font-bold text-[#00FFFF] uppercase">
                5. Complete Operator &amp; Kiosk Manual
              </span>
            </div>
            <p class="text-[11px] text-[#A0A0C0]">
              Explore turnkey multi-display kiosk URL overrides (?density=, ?filter=), committed ticket marking, Telegram morning voice briefs, and Raspberry Pi autostart scripts in Tab 11.
            </p>
          </div>
          <button
            type="button"
            class="px-3 py-1.5 bg-[#000066] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] text-xs font-bold uppercase cursor-pointer shrink-0 transition-colors"
            @click="handleNavigateToGuide"
          >
            [ OPEN TAB 11 GUIDE ]
          </button>
        </div>

        <!-- Footer Dismissal Controls -->
        <div class="pt-3 border-t border-[#FFFF00]/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <!-- Never Show Again Checkbox -->
          <label class="flex items-center space-x-2 cursor-pointer text-xs text-[#E0E0E0] hover:text-[#FFFF00] transition-colors select-none">
            <input
              v-model="neverShowAgain"
              type="checkbox"
              class="w-4 h-4 accent-[#00FF00] cursor-pointer"
            />
            <span class="font-bold uppercase tracking-wider">
              Do Not Show This Welcome Guide Again on Startup
            </span>
          </label>

          <!-- Dismiss / Action Buttons -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              type="button"
              class="px-4 py-2 bg-[#FFFF00] text-[#000033] hover:bg-[#FFFFFF] border-2 border-[#FFFF00] font-black uppercase cursor-pointer shadow-[0_0_12px_rgba(255,255,0,0.8)] transition-all"
              @click="handleDismiss"
            >
              [ START BROADCAST / DISMISS ]
            </button>
          </div>
        </div>

        <!-- Restore Note -->
        <div class="text-[10px] text-[#8888AA] text-center pt-1">
          * You can reopen this guide or reset your startup preference anytime in <strong>Settings &gt; Tab 11 (User Onboarding &amp; Deployment Guide)</strong>.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close', neverShowAgain: boolean): void
}>()

const router = useRouter()
const neverShowAgain = ref(false)

function handleDismiss() {
  emit('close', neverShowAgain.value)
}

function handleNavigateToGuide() {
  emit('close', neverShowAgain.value)
  router.push({ path: '/settings', query: { tab: 'guide' } })
}
</script>
