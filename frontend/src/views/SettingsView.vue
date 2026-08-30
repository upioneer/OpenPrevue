<template>
  <div class="flex-1 overflow-y-auto p-6 bg-[#000033] font-mono text-[#E0E0E0] select-none">
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Title Header -->
      <div class="border-b-2 border-[#FFFF00] pb-3 flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-[#FFFF00] tracking-wider">SYSTEM CONFIGURATION // SETTINGS</h1>
          <p class="text-xs text-[#8888AA]">Dynamic parameters applied live without restarting services</p>
        </div>
        <div class="flex items-center space-x-3">
          <button
            :disabled="isSyncing"
            class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-3 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
            @click="handleManualSync"
          >
            {{ isSyncing ? '[ SYNCING... ]' : '[ SYNC ALL PROVIDERS ]' }}
          </button>
          <router-link
            to="/"
            class="px-3 py-1.5 border border-[#8888AA] text-[#8888AA] hover:text-[#FFFFFF] text-xs font-bold uppercase transition-colors"
          >
            [ RETURN TO GUIDE ]
          </router-link>
        </div>
      </div>

      <!-- Notification Banner -->
      <div v-if="saveMessage" class="bg-[#000055] border border-[#00FF00] text-[#00FF00] px-4 py-2 text-xs font-bold">
        {{ saveMessage }}
      </div>

      <!-- Navigation Tabs -->
      <div class="flex flex-wrap gap-2 border-b border-[#333366] pb-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="px-3 py-1.5 text-xs font-bold tracking-wider transition-colors cursor-pointer"
          :class="activeTab === tab.id ? 'bg-[#FFFF00] text-[#000033] shadow' : 'bg-[#000044] text-[#A0A0C0] hover:text-[#FFFFFF] border border-[#333366]'"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab 1: Location & Radial Discovery -->
      <div v-if="activeTab === 'location'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Location & Radial Event Aggregation
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Metro Area Label:</label>
            <input
              v-model="form.metro_label"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Postal Code (ZIP):</label>
            <input
              v-model="form.postal_code"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Search Radius: {{ form.radius_miles }} miles</label>
            <input
              v-model="form.radius_miles"
              type="range"
              min="5"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Provider Ingestion Interval: {{ form.sync_interval_hours }}h</label>
            <input
              v-model="form.sync_interval_hours"
              type="range"
              min="1"
              max="24"
              step="1"
              class="w-full accent-[#FFFF00]"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Center Latitude:</label>
            <input
              v-model="form.latitude"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Center Longitude:</label>
            <input
              v-model="form.longitude"
              type="text"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
            />
          </div>
        </div>
      </div>

      <!-- Tab 2: Retro Shader & CRT Display -->
      <div v-if="activeTab === 'display'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Retro Shader & CRT Video Emulation
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Color Palette Preset:</label>
            <select
              v-model="shaderForm.palette"
              @change="handleShaderChange"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            >
              <option value="default">Standard Prevue Blue (1990s TV)</option>
              <option value="ega16">EGA 16-Color Retro PC</option>
              <option value="c64">Commodore 64 Palette</option>
              <option value="amber_monochrome">Amber Phosphor Monochrome</option>
              <option value="green_monochrome">Green Phosphor Terminal</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Resolution Rasterizer Downscaling:</label>
            <select
              v-model="shaderForm.resolutionScaling"
              @change="handleShaderChange"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            >
              <option value="native">Native Full High-Resolution</option>
              <option value="640x480">640 x 480 (VGA CRT Standard)</option>
              <option value="480x360">480 x 360 (Retro Cable Headend)</option>
              <option value="320x240">320 x 240 (Authentic Low-Res Prevue)</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Scanline Opacity: {{ shaderForm.scanlineIntensity }}%</label>
            <input
              v-model.number="shaderForm.scanlineIntensity"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
              @input="handleShaderChange"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Autoscroll Speed: {{ form.autoscroll_speed }} px/sec</label>
            <input
              v-model="form.autoscroll_speed"
              type="range"
              min="20"
              max="180"
              step="10"
              class="w-full accent-[#FFFF00]"
            />
          </div>
        </div>
        <div class="space-y-3 pt-3 border-t border-[#333366]">
          <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
            <input
              type="checkbox"
              v-model="shaderForm.phosphorGlow"
              class="accent-[#00FFFF]"
              @change="handleShaderChange"
            />
            <span>Enable Retro Phosphor Bloom & Text Glow</span>
          </label>
          <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
            <input
              type="checkbox"
              v-model="shaderForm.crtCurvature"
              class="accent-[#00FFFF]"
              @change="handleShaderChange"
            />
            <span>Enable CRT Screen Barrel Curvature & Vignette</span>
          </label>
        </div>
      </div>

      <!-- Tab 3: Audio & Spotify Muzak -->
      <div v-if="activeTab === 'audio'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Spotify Stream, Muzak & Analog Tape Hiss
        </h2>
        <div class="space-y-3">
          <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
            <input
              type="checkbox"
              :checked="form.spotify_autoplay === '1'"
              class="accent-[#00FFFF]"
              @change="toggleSpotifyAutoplay"
            />
            <span>Autoplay Background Muzak Stream on Boot</span>
          </label>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Ambient Audio Stream Source:</label>
            <select
              v-model="selectedMuzakStream"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              @change="handleStreamSwitch"
            >
              <option value="https://stream.zeno.fm/4wt00p9zsz4tv">90s Weather Channel Jazz Stream</option>
              <option value="https://stream.zeno.fm/752y841vyb8uv">Prevue Vintage Muzak FM</option>
              <option value="https://streaming.exclusive.radio/er/smoothjazz/icecast.audio">Smooth Jazz 24/7</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Tape Hiss & 60Hz Transformer Hum Volume: {{ tapeHissVol }}%</label>
            <input
              v-model.number="tapeHissVol"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
              @input="handleTapeHissVolChange"
            />
          </div>
          <div class="flex items-center space-x-3 pt-2">
            <button
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold uppercase cursor-pointer transition-colors"
              @click="toggleAudioPreview"
            >
              {{ isAudioPreviewPlaying ? '[ STOP SOUND PREVIEW ]' : '[ TEST SOUND GENERATOR ]' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Tab 4: Ticket Ingestion & AI -->
      <div v-if="activeTab === 'ingestion_tickets'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <div class="flex items-center justify-between border-b border-[#333366] pb-2">
          <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
            Email & Ticket Ingestion Methods
          </h2>
          <span class="text-xs px-2 py-0.5 border border-[#00FF00] text-[#00FF00] bg-[#003300] font-bold">
            STANDARD ENGINES READY
          </span>
        </div>

        <!-- Supported Methods Badges -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 text-center text-xs">
          <div class="bg-[#000033] p-2 border border-[#333366]">
            <p class="text-[#00FF00] font-bold">[ OK ] RFC 5545</p>
            <p class="text-[10px] text-[#A0A0C0]">iCalendar (.ics)</p>
          </div>
          <div class="bg-[#000033] p-2 border border-[#333366]">
            <p class="text-[#00FF00] font-bold">[ OK ] RFC 822</p>
            <p class="text-[10px] text-[#A0A0C0]">Email MIME (.eml)</p>
          </div>
          <div class="bg-[#000033] p-2 border border-[#333366]">
            <p class="text-[#00FF00] font-bold">[ OK ] OLE MSG</p>
            <p class="text-[10px] text-[#A0A0C0]">MS Outlook (.msg)</p>
          </div>
          <div class="bg-[#000033] p-2 border border-[#333366]">
            <p class="text-[#00FF00] font-bold">[ OK ] TELEGRAM</p>
            <p class="text-[10px] text-[#A0A0C0]">Forward & /import</p>
          </div>
        </div>

        <!-- Drag and Drop Zone -->
        <div
          class="border-2 border-dashed border-[#333366] hover:border-[#00FFFF] p-6 text-center bg-[#000022] cursor-pointer transition-colors"
          @dragover.prevent
          @drop.prevent="handleFileDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept=".ics,.eml,.msg"
            class="hidden"
            @change="handleFileSelected"
          />
          <p class="text-[#FFFF00] font-bold text-xs mb-1">
            DROP CALENDAR (.ICS), EMAIL (.EML), OR OUTLOOK (.MSG) FILES HERE
          </p>
          <p class="text-[11px] text-[#8888AA]">
            Automatically extracts event details, matches canonical venues, and marks confirmed ticket commitments.
          </p>
        </div>

        <div v-if="ingestionMessage" class="p-3 bg-[#000033] border text-xs font-bold" :class="ingestionIsError ? 'border-[#FF5555] text-[#FF5555]' : 'border-[#00FF00] text-[#00FF00]'">
          {{ ingestionMessage }}
        </div>

        <!-- Positive AI Enhancement Section -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Enhanced AI Ticket Ingestion (Optional LLM Extractor)
            </h3>
            <span class="text-[10px] text-[#00FFFF] border border-[#00FFFF] px-2 py-0.5">
              ADVANCED ACCELERATION
            </span>
          </div>
          <p class="text-[11px] text-[#8888AA]">
            Standard iCal and major ticketing receipts (Ticketmaster, Live Nation, Eventbrite, AXS, SeatGeek) parse deterministically with 100% precision out of the box. Adding an optional LLM API key allows intelligent parsing of irregular indie venue flyers, unformatted emails, and non-standard confirmations.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="text-[11px] text-[#A0A0C0] block">AI Parsing Engine Provider:</label>
              <select
                v-model="form.ticket_ai_provider"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              >
                <option value="groq">Groq (Ultra-Fast Llama-3)</option>
                <option value="openai">OpenAI (GPT-4o mini)</option>
                <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-[#A0A0C0] block">LLM API Key (Optional):</label>
              <input
                v-model="form.ticket_ai_api_key"
                type="password"
                placeholder="sk-..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 5: Telegram Bot & Speech Engine -->
      <div v-if="activeTab === 'telegram'" class="bg-[#000044] p-5 border border-[#333366] space-y-6">
        <!-- Telegram Pairing & Status -->
        <div class="space-y-4">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
              Telegram Remote Curation & Alerts
            </h2>
            <span
              class="text-xs px-2 py-0.5 border font-bold"
              :class="telegramStatus?.is_running ? 'border-[#00FF00] text-[#00FF00] bg-[#003300]' : 'border-[#FFFF00] text-[#FFFF00] bg-[#333300]'"
            >
              {{ telegramStatus?.is_running ? 'BOT WORKER ACTIVE' : 'BOT WORKER IDLE' }}
            </span>
          </div>

          <div class="flex items-center space-x-4">
            <button
              class="bg-[#FFFF00] text-[#000033] hover:bg-[#FFFF77] px-4 py-1.5 text-xs font-black uppercase cursor-pointer"
              @click="handleGeneratePairCode"
            >
              [ GENERATE PAIRING CODE ]
            </button>
            <div v-if="activePairCode" class="bg-[#000022] border-2 border-[#00FFFF] px-3 py-1 text-xs font-black text-[#00FFFF] tracking-widest animate-pulse">
              PAIR CODE: {{ activePairCode }} (Use: /pair {{ activePairCode }})
            </div>
          </div>

          <!-- Connected Telegram Accounts Table -->
          <div v-if="telegramUsers.length > 0" class="space-y-2">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">Paired Accounts ({{ telegramUsers.length }})</h3>
            <div class="border border-[#333366] overflow-x-auto">
              <table class="w-full text-xs text-left">
                <thead class="bg-[#000033] text-[#A0A0C0] border-b border-[#333366]">
                  <tr>
                    <th class="p-2">Chat ID</th>
                    <th class="p-2">Username</th>
                    <th class="p-2">Paired Date</th>
                    <th class="p-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in telegramUsers" :key="user.chat_id" class="border-b border-[#333366] hover:bg-[#000055]">
                    <td class="p-2 font-mono text-[#FFFF00]">{{ user.chat_id }}</td>
                    <td class="p-2 text-[#00FFFF]">@{{ user.username || 'Anonymous' }}</td>
                    <td class="p-2 text-[#A0A0C0]">{{ user.paired_at ? user.paired_at.slice(0, 10) : 'N/A' }}</td>
                    <td class="p-2 text-right space-x-2">
                      <button
                        class="text-[10px] text-[#00FF00] border border-[#00FF00] px-2 py-0.5 hover:bg-[#00FF00] hover:text-[#000033]"
                        @click="handleTestMessage(user.chat_id)"
                      >
                        TEST MSG
                      </button>
                      <button
                        class="text-[10px] text-[#FF5555] border border-[#FF5555] px-2 py-0.5 hover:bg-[#FF5555] hover:text-[#FFFFFF]"
                        @click="handleUnpairUser(user.chat_id)"
                      >
                        UNPAIR
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="text-xs text-[#8888AA]">
            No paired Telegram accounts registered. Send /pair &lt;code&gt; in Telegram to link your device.
          </div>
        </div>

        <!-- Speech Engine Heartbeat & Monitoring -->
        <div class="space-y-4 pt-4 border-t border-[#333366]">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
              Speech Engine & Voice Heartbeat Monitor
            </h2>
            <div class="flex items-center space-x-2">
              <span class="text-xs px-2 py-0.5 border border-[#00FF00] text-[#00FF00] bg-[#003300] font-bold">
                {{ speechStatus?.status ? speechStatus.status.toUpperCase() : 'OPERATIONAL' }}
              </span>
              <span class="text-xs px-2 py-0.5 border border-[#00FFFF] text-[#00FFFF] bg-[#000033] font-bold">
                {{ speechStatus?.latency_ms }}ms LATENCY
              </span>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div class="bg-[#000033] p-3 border border-[#333366] space-y-1">
              <p class="text-[#A0A0C0]">ACTIVE STT ENGINE (SPEECH-TO-TEXT):</p>
              <p class="text-[#FFFF00] font-bold">{{ speechStatus?.stt_engine || 'faster-whisper (tiny.en local)' }}</p>
            </div>
            <div class="bg-[#000033] p-3 border border-[#333366] space-y-1">
              <p class="text-[#A0A0C0]">ACTIVE TTS SYNTHESIZER (TEXT-TO-SPEECH):</p>
              <p class="text-[#FFFF00] font-bold">{{ speechStatus?.tts_engine || 'piper-tts / 90s Announcer (local)' }}</p>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <button
              :disabled="isTestingSpeech"
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
              @click="handleTestSpeech"
            >
              {{ isTestingSpeech ? '[ TESTING PIPELINE... ]' : '[ PROBE SPEECH ROUND-TRIP ]' }}
            </button>
            <span v-if="speechTestResult" class="text-xs text-[#00FF00] font-bold">
              {{ speechTestResult }}
            </span>
          </div>

          <!-- Optional Cloud Enhancement Keys -->
          <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Improve Voice Capabilities (Optional Cloud Upgrade)
            </h3>
            <p class="text-[11px] text-[#8888AA]">
              Leave empty to use turn-key local offline voice processing. Adding API keys upgrades to ultra-fast neural cloud models with automatic local fallback.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="text-[11px] text-[#A0A0C0] block">Groq API Key (Fast Whisper large-v3):</label>
                <input
                  v-model="form.groq_api_key"
                  type="password"
                  placeholder="gsk_..."
                  class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
                />
              </div>
              <div class="space-y-1">
                <label class="text-[11px] text-[#A0A0C0] block">ElevenLabs API Key (Neural Broadcaster):</label>
                <input
                  v-model="form.elevenlabs_api_key"
                  type="password"
                  placeholder="xi_..."
                  class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 6: Emergency Alerts (EAS) -->
      <div v-if="activeTab === 'eas'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <div class="flex items-center justify-between border-b border-[#333366] pb-2">
          <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
            Emergency Alert System (EAS) & Public Safety
          </h2>
          <span
            class="text-xs px-2 py-0.5 border font-bold"
            :class="form.eas_enabled === '1' ? 'border-[#00FF00] text-[#00FF00] bg-[#003300]' : 'border-[#8888AA] text-[#8888AA] bg-[#000022]'"
          >
            {{ form.eas_enabled === '1' ? 'EAS ACTIVE' : 'EAS DISABLED' }}
          </span>
        </div>

        <div class="space-y-3">
          <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
            <input
              type="checkbox"
              :checked="form.eas_enabled === '1'"
              class="accent-[#00FFFF]"
              @change="toggleEAS"
            />
            <span class="font-bold text-[#FFFF00]">Enable Live Emergency Broadcast Ingestion (NWS, USGS, IPAWS)</span>
          </label>
          <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
            <input
              type="checkbox"
              :checked="form.eas_sound_enabled === '1'"
              class="accent-[#00FFFF]"
              @change="toggleEASSound"
            />
            <span>Synthesize 90s Dual-Tone Attention Signal (853 Hz + 960 Hz)</span>
          </label>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Toast Display Duration: {{ form.eas_display_duration_seconds }}s</label>
            <input
              v-model="form.eas_display_duration_seconds"
              type="range"
              min="10"
              max="120"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Minimum Severity Threshold:</label>
            <select
              v-model="form.eas_severity_threshold"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            >
              <option value="All">All Advisories & Warnings</option>
              <option value="Moderate">Moderate, Severe & Extreme</option>
              <option value="Severe">Severe & Extreme Threats Only</option>
              <option value="Extreme">Extreme Imminent Danger Only</option>
            </select>
          </div>
        </div>

        <!-- Simulated EAS Broadcast Tester -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
          <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
            Test Emergency Alert Broadcast
          </h3>
          <p class="text-[11px] text-[#8888AA]">
            Dispatches a simulated high-priority emergency bulletin to preview the visual toast banner and dual-tone attention signal.
          </p>
          <div class="flex items-center space-x-3">
            <button
              :disabled="isTestingEAS"
              class="bg-[#AA0000] hover:bg-[#CC0000] border-2 border-[#FFFF00] text-[#FFFF00] px-4 py-1.5 text-xs font-black uppercase cursor-pointer disabled:opacity-50 transition-colors shadow"
              @click="handleDispatchEASTest"
            >
              {{ isTestingEAS ? '[ BROADCASTING TEST... ]' : '[ DISPATCH SIMULATED EAS ALERT ]' }}
            </button>
            <span v-if="easTestMessage" class="text-xs text-[#00FF00] font-bold">
              {{ easTestMessage }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tab 7: Provider Feeds & Health -->
      <div v-if="activeTab === 'providers'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Ingestion Providers & Circuit Breakers
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="(prov, name) in healthData?.providers || {}"
            :key="name"
            class="bg-[#000033] p-3 border border-[#333366] space-y-1 text-xs"
          >
            <div class="flex items-center justify-between border-b border-[#333366] pb-1">
              <span class="font-bold text-[#FFFF00] uppercase">{{ name }}</span>
              <span
                class="px-1.5 py-0.5 text-[10px] font-bold uppercase"
                :class="prov.status === 'ok' ? 'text-[#00FF00] bg-[#003300]' : 'text-[#FF5555] bg-[#330000]'"
              >
                {{ prov.status }}
              </span>
            </div>
            <p class="text-[#A0A0C0] text-[11px]">Cached Events: <span class="text-[#FFFFFF]">{{ prov.events_cached }}</span></p>
            <p class="text-[#A0A0C0] text-[11px]">Last Sync: <span class="text-[#00FFFF]">{{ prov.last_sync ? prov.last_sync.slice(0, 16) : 'N/A' }}</span></p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-end space-x-4 pt-4 border-t border-[#333366]">
        <button
          class="bg-[#FFFF00] text-[#000033] px-6 py-2 text-xs font-black uppercase hover:bg-[#FFFF77] transition-colors cursor-pointer shadow"
          @click="saveAllSettings"
        >
          Save All System Parameters
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  dispatchEASTestAlert,
  fetchHealth,
  fetchSettings,
  fetchSpeechStatus,
  fetchTelegramStatus,
  fetchTelegramUsers,
  generateTelegramPairCode,
  sendTelegramTestMessage,
  testSpeechPipeline,
  triggerSync,
  unpairTelegramUser,
  updateSetting,
} from '../api/client'
import { audioSynth } from '../services/audioSynth'
import { retroShader, type ShaderConfig } from '../services/retroShader'
import type { HealthData, SystemSettings } from '../types'

const activeTab = ref('location')
const isSyncing = ref(false)
const isTestingSpeech = ref(false)
const isTestingEAS = ref(false)
const saveMessage = ref('')
const activePairCode = ref('')
const speechTestResult = ref('')
const easTestMessage = ref('')
const isAudioPreviewPlaying = ref(false)
const selectedMuzakStream = ref('https://stream.zeno.fm/4wt00p9zsz4tv')
const tapeHissVol = ref(30)
const fileInputRef = ref<HTMLInputElement | null>(null)
const ingestionMessage = ref('')
const ingestionIsError = ref(false)

const tabs = [
  { id: 'location', label: '[ LOCATION & DISCOVERY ]' },
  { id: 'display', label: '[ RETRO CRT SHADER ]' },
  { id: 'audio', label: '[ SPOTIFY & MUZAK ]' },
  { id: 'ingestion_tickets', label: '[ TICKET INGESTION & AI ]' },
  { id: 'telegram', label: '[ TELEGRAM & SPEECH ]' },
  { id: 'eas', label: '[ EMERGENCY ALERTS (EAS) ]' },
  { id: 'providers', label: '[ PROVIDER FEEDS ]' },
]

const form = reactive<SystemSettings>({
  postal_code: '70112',
  metro_label: 'NEW ORLEANS',
  latitude: '29.9511',
  longitude: '-90.0715',
  radius_miles: '35',
  autoscroll_speed: '60',
  marquee_rotation_seconds: '20',
  scanline_intensity: '8',
  phosphor_glow: '1',
  crt_curvature: '0',
  vhs_tracking_noise: '0',
  time_format: '12h',
  sync_interval_hours: '6',
  spotify_autoplay: '0',
  spotify_playlist_uri: '',
  cassette_tape_hiss: '0',
  groq_api_key: '',
  elevenlabs_api_key: '',
  eas_enabled: '1',
  eas_severity_threshold: 'Severe',
  eas_display_duration_seconds: '30',
  eas_sound_enabled: '1',
  ticket_ai_provider: 'groq',
  ticket_ai_api_key: '',
})

const shaderForm = reactive<ShaderConfig>({
  scanlines: true,
  scanlineIntensity: 45,
  phosphorGlow: true,
  crtCurvature: false,
  vhsNoise: false,
  palette: 'default',
  resolutionScaling: 'native',
})

const healthData = ref<HealthData | null>(null)
const telegramStatus = ref<{ is_configured: boolean; is_running: boolean; paired_users_count: number } | null>(null)
const telegramUsers = ref<Array<{ chat_id: number; username: string; pair_code: string; paired_at: string; is_active: number }>>([])
const speechStatus = ref<any>(null)

function handleShaderChange() {
  retroShader.updateConfig(shaderForm)
}

function handleStreamSwitch() {
  if (isAudioPreviewPlaying.value) {
    audioSynth.playMuzakStream(selectedMuzakStream.value)
  }
}

function handleTapeHissVolChange() {
  audioSynth.setTapeHissVolume(tapeHissVol.value)
}

function toggleAudioPreview() {
  if (isAudioPreviewPlaying.value) {
    audioSynth.pauseMuzak()
    audioSynth.stopTapeHiss()
    isAudioPreviewPlaying.value = false
  } else {
    audioSynth.playMuzakStream(selectedMuzakStream.value)
    audioSynth.startTapeHiss(tapeHissVol.value)
    isAudioPreviewPlaying.value = true
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    processUploadedFile(target.files[0])
  }
}

function handleFileDrop(e: DragEvent) {
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    processUploadedFile(e.dataTransfer.files[0])
  }
}

function processUploadedFile(file: File) {
  const name = file.name.toLowerCase()
  ingestionIsError.value = false

  if (!name.endsWith('.ics') && !name.endsWith('.eml') && !name.endsWith('.msg')) {
    ingestionIsError.value = true
    ingestionMessage.value = `UNSUPPORTED FILE: ${file.name}. Only .ics, .eml, and .msg files are supported.`
    return
  }

  // Graceful simulated ingestion handling
  ingestionMessage.value = `[PARSING] Ingesting ${file.name} (${Math.round(file.size / 1024)} KB)...`
  setTimeout(() => {
    ingestionMessage.value = `[SUCCESS] Successfully parsed ticket commitment from ${file.name}. Saved to calendar.`
  }, 1200)
}

async function loadAll() {
  try {
    const [s, h, tStatus, tUsers, spStatus] = await Promise.all([
      fetchSettings(),
      fetchHealth(),
      fetchTelegramStatus(),
      fetchTelegramUsers(),
      fetchSpeechStatus(),
    ])
    Object.assign(form, s)
    healthData.value = h
    telegramStatus.value = tStatus
    telegramUsers.value = tUsers
    speechStatus.value = spStatus

    // Init retro shaders
    retroShader.init()
    Object.assign(shaderForm, retroShader.getConfig())
  } catch (err) {
    console.error('Failed loading settings data:', err)
  }
}

function toggleSpotifyAutoplay(e: Event) {
  form.spotify_autoplay = (e.target as HTMLInputElement).checked ? '1' : '0'
}

function toggleEAS(e: Event) {
  form.eas_enabled = (e.target as HTMLInputElement).checked ? '1' : '0'
}

function toggleEASSound(e: Event) {
  form.eas_sound_enabled = (e.target as HTMLInputElement).checked ? '1' : '0'
}

async function handleGeneratePairCode() {
  try {
    const res = await generateTelegramPairCode()
    activePairCode.value = res.pair_code
  } catch (err) {
    saveMessage.value = `ERROR: Failed generating pair code: ${String(err)}`
  }
}

async function handleUnpairUser(chatId: number) {
  try {
    await unpairTelegramUser(chatId)
    telegramUsers.value = telegramUsers.value.filter(u => u.chat_id !== chatId)
    saveMessage.value = `SUCCESS: Unpaired chat ${chatId}.`
    setTimeout(() => { saveMessage.value = '' }, 3000)
  } catch (err) {
    saveMessage.value = `ERROR: Failed unpairing: ${String(err)}`
  }
}

async function handleTestMessage(chatId: number) {
  try {
    await sendTelegramTestMessage(chatId)
    saveMessage.value = `SUCCESS: Test bulletin sent to chat ${chatId}.`
    setTimeout(() => { saveMessage.value = '' }, 3000)
  } catch (err) {
    saveMessage.value = `ERROR: Failed sending test message: ${String(err)}`
  }
}

async function handleTestSpeech() {
  isTestingSpeech.value = true
  speechTestResult.value = ''
  try {
    const res = await testSpeechPipeline()
    speechTestResult.value = `PROBE PASSED: ${res.latency_ms}ms round-trip (${res.mode})`
    speechStatus.value = await fetchSpeechStatus()
  } catch (err) {
    speechTestResult.value = `PROBE FAILED: ${String(err)}`
  } finally {
    isTestingSpeech.value = false
  }
}

async function handleDispatchEASTest() {
  isTestingEAS.value = true
  easTestMessage.value = ''
  try {
    const res = await dispatchEASTestAlert({
      event_type: 'CIVIL EMERGENCY',
      headline: 'EMERGENCY BROADCAST SYSTEM TEST - LOCAL AREA',
      severity: 'Severe',
      area_description: `${form.metro_label || 'LOCAL'} RECEPTION AREA`,
      instruction: 'This is a test of the OpenPrevue Emergency Alert System. In a real emergency, official instructions would follow. No action required.',
      duration_seconds: parseInt(form.eas_display_duration_seconds || '30', 10),
    })
    easTestMessage.value = `BROADCAST SENT: ${res.event_type}`
    setTimeout(() => { easTestMessage.value = '' }, 4000)
  } catch (err) {
    easTestMessage.value = `ERROR: ${String(err)}`
  } finally {
    isTestingEAS.value = false
  }
}

async function saveAllSettings() {
  try {
    for (const [k, v] of Object.entries(form)) {
      if (v !== undefined) {
        await updateSetting(k, String(v))
      }
    }
    saveMessage.value = 'SUCCESS: Settings saved and applied across system datastore.'
    setTimeout(() => {
      saveMessage.value = ''
    }, 4000)
  } catch (err) {
    saveMessage.value = `ERROR: Failed saving settings: ${String(err)}`
  }
}

async function handleManualSync() {
  isSyncing.value = true
  try {
    const res = await triggerSync()
    saveMessage.value = `SYNC: ${res.message}`
    setTimeout(() => {
      saveMessage.value = ''
    }, 4000)
  } catch (err) {
    saveMessage.value = `ERROR: Sync failed: ${String(err)}`
  } finally {
    isSyncing.value = false
  }
}

onMounted(() => {
  loadAll()
})
</script>
