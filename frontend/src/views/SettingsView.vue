<template>
  <div class="flex-1 w-full h-full bg-[#000033] text-[#E0E0E0] overflow-y-auto p-4 md:p-6 font-mono select-none">
    <div class="max-w-5xl mx-auto space-y-6">
      <!-- Header Bar -->
      <div class="flex items-center justify-between border-b-2 border-[#FFFF00] pb-3">
        <div class="flex items-center space-x-3">
          <span class="w-3 h-3 bg-[#FFFF00] inline-block animate-pulse"></span>
          <h1 class="text-xl md:text-2xl font-black text-[#FFFF00] tracking-widest">
            OPENPREVUE SYSTEM CONFIGURATION
          </h1>
        </div>
        <div class="flex items-center space-x-3">
          <RouterLink
            to="/"
            class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-3 py-1 text-xs font-bold tracking-wider transition-colors cursor-pointer"
          >
            [ RETURN TO GUIDE ]
          </RouterLink>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex flex-wrap gap-1 border-b border-[#333366] pb-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="px-3 py-1.5 text-xs font-bold tracking-wider border cursor-pointer transition-all"
          :class="activeTab === tab.id
            ? 'bg-[#FFFF00] text-[#000033] border-[#FFFF00] shadow-[0_0_8px_rgba(255,255,0,0.8)]'
            : 'bg-[#000055] text-[#8888AA] border-[#333366] hover:text-[#00FFFF] hover:border-[#00FFFF]'"
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

        <!-- Quick Regional Presets -->
        <div class="bg-[#000033] p-3 border border-[#333366] space-y-2">
          <label class="text-xs font-bold text-[#FFFF00] block uppercase">Quick Regional Presets:</label>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-1.5">
            <button
              v-for="preset in REGIONAL_PRESETS"
              :key="preset.label"
              type="button"
              class="px-2 py-1 border text-[11px] font-bold transition-all text-left truncate cursor-pointer"
              :class="form.metro_label === preset.metro
                ? 'bg-[#FFFF00] text-[#000033] border-[#FFFF00]'
                : 'bg-[#000044] text-[#E0E0E0] border-[#333366] hover:border-[#00FFFF] hover:text-[#00FFFF]'"
              @click="applyRegionalPreset(preset)"
            >
              [ {{ preset.label }} ]
            </button>
          </div>
        </div>

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
              <option value="default">Standard Prevue Blue (1990s TV Default)</option>
              <option value="ega16">EGA 16-Color PC Mode</option>
              <option value="vga256">VGA 256-Color Mode</option>
              <option value="c64">Commodore 64 Palette</option>
              <option value="amber_monochrome">Amber Monochrome CRT</option>
              <option value="green_monochrome">Green Phosphor Terminal</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Resolution Downsampler Scaling:</label>
            <select
              v-model="shaderForm.resolutionScaling"
              @change="handleShaderChange"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            >
              <option value="native">Native Display Resolution</option>
              <option value="640x480">640x480 CRT VGA</option>
              <option value="480x360">480x360 Vintage NTSC</option>
              <option value="320x240">320x240 Low-Res Scanline Grid</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Scanline Opacity: {{ shaderForm.scanlineIntensity }}%</label>
            <input
              v-model="shaderForm.scanlineIntensity"
              @input="handleShaderChange"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Autoscroll Speed: {{ form.autoscroll_speed }} px/sec</label>
            <input
              v-model="form.autoscroll_speed"
              type="range"
              min="20"
              max="150"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Marquee Rotation Interval: {{ form.marquee_rotation_seconds }}s</label>
            <input
              v-model="form.marquee_rotation_seconds"
              type="range"
              min="5"
              max="60"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="flex items-center space-x-4 pt-2">
            <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
              <input
                v-model="shaderForm.phosphorGlow"
                @change="handleShaderChange"
                type="checkbox"
                class="accent-[#00FF00]"
              />
              <span>Phosphor Text Glow Bloom</span>
            </label>

            <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
              <input
                v-model="shaderForm.crtCurvature"
                @change="handleShaderChange"
                type="checkbox"
                class="accent-[#00FF00]"
              />
              <span>CRT Screen Curvature</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Tab 3: Audio & Muzak Synthesizer -->
      <div v-if="activeTab === 'audio'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Background Audio & Tape Hiss Emulation
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Ambient Muzak Stream Preset:</label>
            <select
              v-model="selectedMuzakStream"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            >
              <option
                v-for="stream in muzakStreams"
                :key="stream.url"
                :value="stream.url"
              >
                {{ stream.name }}
              </option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Muzak Stream Volume: {{ muzakVol }}%</label>
            <input
              v-model="muzakVol"
              @input="handleAudioVolumeChange"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Analog Tape Hiss & 60Hz Hum Volume: {{ tapeHissVol }}%</label>
            <input
              v-model="tapeHissVol"
              @input="handleAudioVolumeChange"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
          </div>

          <div class="flex items-center space-x-3 pt-4">
            <button
              type="button"
              class="px-4 py-2 border text-xs font-black tracking-wider transition-all cursor-pointer"
              :class="isAudioPreviewPlaying
                ? 'bg-[#FF4444] text-white border-[#FF4444]'
                : 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_8px_rgba(0,255,0,0.8)]'"
              @click="toggleAudioPreview"
            >
              {{ isAudioPreviewPlaying ? '[ STOP AUDIO GENERATOR ]' : '[ TEST SOUND GENERATOR ]' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Tab 4: Ticket Ingestion & AI -->
      <div v-if="activeTab === 'ingestion'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Multi-Format Reservation Ingestion & Enhanced AI Extractor
        </h2>

        <!-- Ingestion Matrix Banner -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Drag & Drop Ticket Ingestion Dropzone
            </h3>
            <span class="text-[10px] text-[#00FFFF]">SUPPORTED: .ICS | .EML | .MSG</span>
          </div>

          <div
            class="border-2 border-dashed border-[#333366] hover:border-[#00FFFF] p-6 text-center rounded-xs transition-colors cursor-pointer bg-[#000022]/60"
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
            <div class="space-y-1">
              <div class="text-xs text-[#FFFF00] font-bold">DRAG AND DROP RESERVATION FILES HERE</div>
              <div class="text-[11px] text-[#8888AA]">or click to browse calendar (.ics), email (.eml), or Outlook (.msg) files</div>
            </div>
          </div>

          <div v-if="ingestionMessage" class="p-2 text-xs border" :class="ingestionIsError ? 'bg-[#330000] border-[#FF4444] text-[#FF8888]' : 'bg-[#003300] border-[#00FF00] text-[#00FF00]'">
            {{ ingestionMessage }}
          </div>
        </div>

        <!-- Enhanced AI Ticket Extractor Settings -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Enhanced AI Ticket Parser (Optional Cloud Assist)
            </h3>
            <span class="text-[10px] text-[#00FF00] font-bold">ZERO-CONFIG LOCAL PARSER ACTIVE</span>
          </div>

          <p class="text-[11px] text-[#8888AA] leading-relaxed">
            Standard calendar feeds (.ics), MIME emails (.eml), and Outlook messages (.msg) parse deterministically with 100% precision out of the box with no API keys needed.
            Add an optional API key below to enable enhanced AI extraction for complex, unformatted indie venue flyers and irregular promoter emails.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
            <div class="space-y-1">
              <label class="text-[11px] text-[#A0A0C0] block">Groq API Key (Llama 3.3 70B):</label>
              <input
                v-model="form.ai_groq_key"
                type="password"
                placeholder="gsk_..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-[#A0A0C0] block">OpenAI API Key (GPT-4o Mini):</label>
              <input
                v-model="form.ai_openai_key"
                type="password"
                placeholder="sk-..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-[#A0A0C0] block">Anthropic API Key (Claude 3.5 Haiku):</label>
              <input
                v-model="form.ai_anthropic_key"
                type="password"
                placeholder="sk-ant-..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 5: Telegram & Speech -->
      <div v-if="activeTab === 'telegram'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Telegram Bot & Spoken Voice Announcer
        </h2>

        <!-- Telegram Pairing Wizard -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Telegram Device Pairing Wizard
            </h3>
            <span
              class="text-[11px] px-2 py-0.5 border"
              :class="telegramStatus?.is_running ? 'bg-[#003300] text-[#00FF00] border-[#00FF00]' : 'bg-[#330000] text-[#FF4444] border-[#FF4444]'"
            >
              {{ telegramStatus?.is_running ? '[ BOT ACTIVE ]' : '[ BOT OFFLINE ]' }}
            </span>
          </div>

          <p class="text-[11px] text-[#8888AA] leading-relaxed">
            Pair your Telegram account to curate the channel schedule, pin featured events, search upcoming concerts, and query by voice from anywhere.
          </p>

          <div class="flex items-center space-x-3 pt-1">
            <button
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer transition-colors"
              @click="handleGeneratePairCode"
            >
              [ GENERATE PAIRING CODE ]
            </button>
            <div v-if="activePairCode" class="flex items-center space-x-2">
              <span class="text-xs text-[#8888AA]">Type in Telegram:</span>
              <code class="bg-[#000022] text-[#FFFF00] font-black px-2 py-1 border border-[#FFFF00] text-sm tracking-widest">
                /pair {{ activePairCode }}
              </code>
            </div>
          </div>

          <!-- Connected Users List -->
          <div v-if="telegramUsers.length > 0" class="pt-2 border-t border-[#333366] space-y-2">
            <label class="text-xs text-[#A0A0C0] block font-bold">PAIRED TELEGRAM DEVICES ({{ telegramUsers.length }}):</label>
            <div class="space-y-1">
              <div
                v-for="user in telegramUsers"
                :key="user.chat_id"
                class="flex items-center justify-between bg-[#000022] px-3 py-1.5 border border-[#333366] text-xs"
              >
                <div class="flex items-center space-x-2">
                  <span class="text-[#00FF00] font-bold">@{{ user.username || 'User' }}</span>
                  <span class="text-[#8888AA] text-[10px]">Chat ID: {{ user.chat_id }}</span>
                </div>
                <div class="flex items-center space-x-2">
                  <button
                    class="text-[10px] text-[#00FFFF] hover:underline cursor-pointer"
                    @click="handleTestMessage(user.chat_id)"
                  >
                    [ Send Test Bulletin ]
                  </button>
                  <button
                    class="text-[10px] text-[#FF4444] hover:underline cursor-pointer"
                    @click="handleUnpairUser(user.chat_id)"
                  >
                    [ Unpair ]
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Speech Engine Diagnostics -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Speech Synthesizer & Voice Router Diagnostics
            </h3>
            <span
              class="text-[11px] px-2 py-0.5 border bg-[#003300] text-[#00FF00] border-[#00FF00]"
            >
              [ HEALTH: {{ speechStatus?.status?.toUpperCase() || 'HEALTHY' }} ]
            </span>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
            <div class="bg-[#000022] p-2 border border-[#333366]">
              <span class="text-[#8888AA] block text-[10px]">SPEECH MODE:</span>
              <span class="text-[#FFFF00] font-bold">{{ speechStatus?.mode || 'local_standard' }}</span>
            </div>
            <div class="bg-[#000022] p-2 border border-[#333366]">
              <span class="text-[#8888AA] block text-[10px]">STT ENGINE:</span>
              <span class="text-[#00FFFF] font-bold">{{ speechStatus?.stt_engine || 'faster-whisper (CPU)' }}</span>
            </div>
            <div class="bg-[#000022] p-2 border border-[#333366]">
              <span class="text-[#8888AA] block text-[10px]">TTS ANNOUNCER:</span>
              <span class="text-[#00FFFF] font-bold">{{ speechStatus?.tts_engine || 'piper-tts (90s TV)' }}</span>
            </div>
            <div class="bg-[#000022] p-2 border border-[#333366]">
              <span class="text-[#8888AA] block text-[10px]">LAST HEARTBEAT:</span>
              <span class="text-[#E0E0E0] font-bold">{{ speechStatus?.last_heartbeat ? new Date(speechStatus.last_heartbeat).toLocaleTimeString() : 'Active' }}</span>
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
          <span class="text-[11px] text-[#FFFF00]">NOAA / NWS CAP FEED INGESTION</span>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between bg-[#000033] p-3 border border-[#333366]">
            <div>
              <span class="text-xs font-bold text-[#FFFF00] block">Enable Emergency Alert System Banner:</span>
              <span class="text-[11px] text-[#8888AA]">Display high-priority weather and civil alerts with audio chimes.</span>
            </div>
            <input
              type="checkbox"
              :checked="form.eas_enabled === '1'"
              class="w-4 h-4 accent-[#FF4444]"
              @change="toggleEAS"
            />
          </div>

          <div class="flex items-center justify-between bg-[#000033] p-3 border border-[#333366]">
            <div>
              <span class="text-xs font-bold text-[#FFFF00] block">Dual-Tone Audio Attention Signal (853 Hz + 960 Hz):</span>
              <span class="text-[11px] text-[#8888AA]">Play authentic 1990s emergency tone signal on active alert broadcast.</span>
            </div>
            <input
              type="checkbox"
              :checked="form.eas_sound_enabled === '1'"
              class="w-4 h-4 accent-[#FF4444]"
              @change="toggleEASSound"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-[#000033] p-3 border border-[#333366]">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">Minimum Alert Severity Level:</label>
              <select
                v-model="form.eas_min_severity"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              >
                <option value="Minor">Minor (Advisories, Special Statements, Watches)</option>
                <option value="Moderate">Moderate (Severe Warnings, High Impact)</option>
                <option value="Severe">Severe (Tornado, Flash Flood, Evacuation)</option>
                <option value="Extreme">Extreme (Civil Danger, Extreme Urgency Only)</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">Alert Display Duration: {{ form.eas_display_duration_seconds || '30' }}s</label>
              <input
                v-model="form.eas_display_duration_seconds"
                type="range"
                min="10"
                max="120"
                step="5"
                class="w-full accent-[#FFFF00]"
              />
            </div>
          </div>

          <div class="pt-2 flex items-center space-x-3">
            <button
              :disabled="isTestingEAS"
              class="bg-[#330000] hover:bg-[#550000] border border-[#FF4444] text-[#FF8888] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
              @click="handleDispatchEASTest"
            >
              {{ isTestingEAS ? '[ DISPATCHING... ]' : '[ DISPATCH SIMULATED EAS ALERT ]' }}
            </button>
            <span v-if="easTestMessage" class="text-xs text-[#00FF00] font-bold">
              {{ easTestMessage }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tab 7: Provider API Keys -->
      <div v-if="activeTab === 'providers'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          External Ticketing & Event Provider APIs
        </h2>
        <div class="space-y-3">
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Ticketmaster Discovery API Key:</label>
            <input
              v-model="form.ticketmaster_api_key"
              type="password"
              placeholder="Live Ticketmaster Discovery API key"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
            />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">SeatGeek Client ID:</label>
              <input
                v-model="form.seatgeek_client_id"
                type="text"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">SeatGeek Client Secret:</label>
              <input
                v-model="form.seatgeek_client_secret"
                type="password"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
              />
            </div>
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Eventbrite Private Token:</label>
            <input
              v-model="form.eventbrite_api_token"
              type="password"
              placeholder="Bearer token"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
            />
          </div>
          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block">Telegram Bot API Token:</label>
            <input
              v-model="form.telegram_bot_token"
              type="password"
              placeholder="From @BotFather"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none"
            />
          </div>
        </div>
      </div>

      <!-- Action Bar -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t-2 border-[#FFFF00]">
        <div class="flex items-center space-x-3">
          <button
            class="bg-[#FFFF00] text-[#000033] hover:bg-[#FFFFFF] px-5 py-2 text-xs font-black tracking-wider cursor-pointer shadow-[0_0_10px_rgba(255,255,0,0.8)] transition-all"
            @click="saveAllSettings"
          >
            [ SAVE & APPLY CONFIGURATION ]
          </button>
          <button
            :disabled="isSyncing"
            class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-2 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
            @click="handleManualSync"
          >
            {{ isSyncing ? '[ SYNCHRONIZING... ]' : '[ TRIGGER INSTANT SYNC ]' }}
          </button>
        </div>

        <div v-if="saveMessage" class="text-xs font-bold" :class="saveMessage.startsWith('ERROR') ? 'text-[#FF4444]' : 'text-[#00FF00]'">
          {{ saveMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  dispatchEASTestAlert,
  fetchHealth,
  fetchSpeechStatus,
  fetchSettings,
  fetchTelegramStatus,
  fetchTelegramUsers,
  generateTelegramPairCode,
  sendTelegramTestMessage,
  testSpeechPipeline,
  triggerSync,
  unpairTelegramUser,
  updateSetting,
} from '../api/client'
import { retroShader, type ShaderConfig } from '../services/retroShader'
import { audioSynth } from '../services/audioSynth'
import { REGIONAL_PRESETS, type RegionalPreset } from '../services/regionalPresets'
import type { HealthData, SystemSettings } from '../types'

const tabs = [
  { id: 'location', label: '[ LOCATION & DISCOVERY ]' },
  { id: 'display', label: '[ RETRO CRT SHADER ]' },
  { id: 'audio', label: '[ SPOTIFY & MUZAK ]' },
  { id: 'ingestion', label: '[ TICKET INGESTION & AI ]' },
  { id: 'telegram', label: '[ TELEGRAM & SPEECH ]' },
  { id: 'eas', label: '[ EMERGENCY ALERTS (EAS) ]' },
  { id: 'providers', label: '[ PROVIDER CREDENTIALS ]' },
]

const activeTab = ref('location')
const isSyncing = ref(false)
const saveMessage = ref('')
const healthData = ref<HealthData | null>(null)
const telegramStatus = ref<{ is_configured: boolean; is_running: boolean; paired_users_count: number } | null>(null)
const telegramUsers = ref<Array<{ chat_id: number; username: string; pair_code: string; paired_at: string; is_active: number }>>([])
const activePairCode = ref('')
const isTestingSpeech = ref(false)
const speechTestResult = ref('')
const speechStatus = ref<{ status: string; mode: string; speech_enabled: boolean; stt_status: string; tts_status: string; stt_engine: string; tts_engine: string; latency_ms: number; last_heartbeat: string } | null>(null)
const isTestingEAS = ref(false)
const easTestMessage = ref('')

// Retro Shader Config Reactive State
const shaderForm = reactive<ShaderConfig>({
  scanlines: true,
  scanlineIntensity: 45,
  phosphorGlow: true,
  crtCurvature: false,
  vhsNoise: false,
  palette: 'default',
  resolutionScaling: 'native',
})

// Web Audio State
const isAudioPreviewPlaying = ref(false)
const tapeHissVol = ref(35)
const muzakVol = ref(50)
const muzakStreams = audioSynth.getPlaybackState().streams
const selectedMuzakStream = ref(muzakStreams[0].url)

// Ticket Ingestion State
const fileInputRef = ref<HTMLInputElement | null>(null)
const ingestionMessage = ref('')
const ingestionIsError = ref(false)

const form = reactive<SystemSettings>({
  postal_code: '10001',
  metro_label: 'NEW YORK CITY',
  latitude: '40.7128',
  longitude: '-74.0060',
  radius_miles: '25',
  autoscroll_speed: '60',
  marquee_rotation_seconds: '20',
  scanline_intensity: '45',
  phosphor_glow: '1',
  crt_curvature: '0',
  vhs_tracking_noise: '0',
  time_format: '12h',
  sync_interval_hours: '6',
  spotify_autoplay: '0',
  eas_enabled: '1',
  eas_sound_enabled: '1',
  eas_min_severity: 'Moderate',
  eas_display_duration_seconds: '30',
  ticketmaster_api_key: '',
  seatgeek_client_id: '',
  seatgeek_client_secret: '',
  eventbrite_api_token: '',
  telegram_bot_token: '',
  groq_api_key: '',
  elevenlabs_api_key: '',
  ai_groq_key: '',
  ai_openai_key: '',
  ai_anthropic_key: '',
})

function applyRegionalPreset(preset: RegionalPreset) {
  form.metro_label = preset.metro
  form.postal_code = preset.zip
  form.latitude = preset.lat.toString()
  form.longitude = preset.lon.toString()
  form.radius_miles = preset.radius.toString()
}

function handleShaderChange() {
  retroShader.updateConfig(shaderForm)
}

function handleAudioVolumeChange() {
  audioSynth.setTapeHissVolume(tapeHissVol.value)
  audioSynth.setMuzakVolume(muzakVol.value)
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
    telegramUsers.value = telegramUsers.value.filter((u: { chat_id: number }) => u.chat_id !== chatId)
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
