<template>
  <header class="h-8 bg-[#000044] border-b border-[#333366] flex items-center justify-between px-4 text-xs font-mono select-none">
    <div class="flex items-center space-x-3">
      <router-link to="/" class="font-bold tracking-wider text-[#FFFF00] hover:underline">
        OPENPREVUE // CHANNEL GUIDE
      </router-link>
      <span class="text-[#8888AA]">|</span>
      <span class="text-[#00FFFF]">LIVE BROADCAST</span>
    </div>

    <div class="flex items-center space-x-4">
      <router-link
        to="/"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors"
        :class="{ 'text-[#FFFF00] font-bold': $route.path === '/' }"
      >
        [ GUIDE ]
      </router-link>
      <router-link
        to="/settings"
        class="text-[#E0E0E0] hover:text-[#FFFF00] transition-colors"
        :class="{ 'text-[#FFFF00] font-bold': $route.path === '/settings' }"
      >
        [ SETTINGS ]
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
// Header bar component
</script>
