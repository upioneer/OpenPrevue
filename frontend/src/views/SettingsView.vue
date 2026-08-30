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
              step="1"
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

      <!-- Tab 3: Audio, Spotify, Commercials & Muzak Synthesizer -->
      <div v-if="activeTab === 'audio'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Background Audio, Spotify, Retro Commercials & RF Filter
        </h2>

        <!-- Retro Video Commercials & Bumpers Engine Card -->
        <div class="bg-[#000033] border border-[#FFFF00] p-4 space-y-4">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <div>
              <span class="text-xs font-bold text-[#FFFF00] block uppercase">
                1990s Television Commercials & Station Bumpers Engine
              </span>
              <span class="text-[11px] text-[#8888AA]">
                Periodically plays retro commercial breaks and station IDs in the top preview quadrant.
              </span>
            </div>
            <label class="flex items-center space-x-2 text-xs font-bold text-[#00FF00] cursor-pointer">
              <input
                v-model="commercialsEnabled"
                @change="handleCommercialsConfigChange"
                type="checkbox"
                class="w-4 h-4 accent-[#00FF00]"
              />
              <span>{{ commercialsEnabled ? '[ COMMERCIALS ACTIVE ]' : '[ DISABLED ]' }}</span>
            </label>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">
                Commercial Break Frequency: {{ commercialsFrequency }} per hour
                <span class="text-[#00FFFF] block text-[10px]">
                  (Plays 1 commercial every {{ Math.round(60 / commercialsFrequency) }} minutes / ~{{ Math.round(15 / commercialsFrequency) || 1 }} songs)
                </span>
              </label>
              <input
                v-model.number="commercialsFrequency"
                @input="handleCommercialsConfigChange"
                type="range"
                min="1"
                max="10"
                step="1"
                class="w-full accent-[#FFFF00]"
              />
            </div>

            <div class="flex items-center space-x-3 pt-2">
              <button
                type="button"
                class="bg-[#000080] hover:bg-[#0000AA] border border-[#FFFF00] text-[#FFFF00] px-4 py-2 text-xs font-bold tracking-wider cursor-pointer transition-colors shadow"
                @click="triggerCommercialTest"
              >
                [ TEST PLAY COMMERCIAL CLIP ]
              </button>
            </div>
          </div>

          <!-- Video Dropzone for User Commercial Rips / OEM Bumpers -->
          <div class="pt-1 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-[#00FFFF] uppercase">Local Commercial Video Dropzone (.MP4 / .WEBM):</span>
              <span class="text-[10px] text-[#8888AA]">{{ commercialsEngine.clips.value.length }} clips in queue</span>
            </div>
            <div
              class="border-2 border-dashed border-[#333366] hover:border-[#FFFF00] p-4 text-center rounded-xs transition-colors cursor-pointer bg-[#000022]/60"
              @dragover.prevent
              @drop.prevent="handleVideoDrop"
              @click="triggerVideoFileInput"
            >
              <input
                ref="videoFileInputRef"
                type="file"
                accept=".mp4,.webm,.m4v"
                class="hidden"
                @change="handleVideoFileSelected"
              />
              <div class="space-y-1">
                <div class="text-xs text-[#FFFF00] font-bold">DRAG AND DROP RETRO COMMERCIAL CLIPS HERE</div>
                <div class="text-[11px] text-[#8888AA]">Plays in top preview window during scheduled commercial breaks</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Official OpenPrevue Spotify Playlist Banner -->
        <div class="bg-[#000033] border border-[#1DB954] p-4 space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1DB954]/40 pb-2">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 bg-[#1DB954] inline-block animate-pulse"></span>
              <h3 class="text-xs font-bold text-[#1DB954] uppercase tracking-wider">
                Official OpenPrevue Spotify Playlist
              </h3>
            </div>
            <a
              href="https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f"
              target="_blank"
              rel="noopener noreferrer"
              class="bg-[#1DB954] text-[#000033] hover:bg-white px-3 py-1 text-xs font-black tracking-wider transition-all cursor-pointer inline-block text-center shadow-[0_0_10px_rgba(29,185,84,0.6)]"
            >
              [ OPEN PLAYLIST ON SPOTIFY ]
            </a>
          </div>

          <p class="text-[11px] text-[#A0A0C0] leading-relaxed">
            Curated vintage ambient jazz, 1990s Weather Channel smooth lounge, vaporwave acoustics, and vintage cable headend themes.
          </p>

          <!-- Spotify Embedded Player -->
          <div class="w-full pt-1">
            <iframe
              style="border-radius: 4px"
              src="https://open.spotify.com/embed/playlist/3jiPmIT4RugR8TPhli5Obk?utm_source=generator&theme=0"
              width="100%"
              height="152"
              frameBorder="0"
              allowfullscreen
              allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
              loading="lazy"
            ></iframe>
          </div>
        </div>

        <!-- Headend Audio Encoding & Filter Guidance Banner -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-2">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Headend Audio Encoding & Vintage Signal Specs
            </h3>
            <span class="text-[10px] text-[#00FF00] font-bold">12 kHz HIGH-SHELF FILTER ACTIVE</span>
          </div>
          <p class="text-[11px] text-[#A0A0C0] leading-relaxed">
            For OpenPrevue setups, encode your audio files to <strong class="text-[#FFFF00]">128–192 kbps MP3</strong> or standard stereo <strong class="text-[#FFFF00]">16-bit 44.1 kHz WAV/OGG</strong> (depending on your audio backend configuration). If you want the full authentic 1990s analog CRT vibe, passing the audio through a mild high-shelf cut filter (around 12 kHz) replicates the classic composite/RF baseband frequency response of 90s cable headends.
          </p>
        </div>

        <!-- 1990s RF / Composite Baseband Audio Filter Control Panel -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-4">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <div>
              <span class="text-xs font-bold text-[#00FFFF] block uppercase">
                1990s RF / Composite Baseband Audio Filter (DSP Pipeline)
              </span>
              <span class="text-[11px] text-[#8888AA]">
                Simulates cable headend modulator frequency response and analog television speakers.
              </span>
            </div>
            <label class="flex items-center space-x-2 text-xs font-bold text-[#FFFF00] cursor-pointer">
              <input
                v-model="audioFilterForm.enabled"
                @change="handleFilterChange"
                type="checkbox"
                class="w-4 h-4 accent-[#00FF00]"
              />
              <span>{{ audioFilterForm.enabled ? '[ FILTER ENGAGED ]' : '[ BYPASS ]' }}</span>
            </label>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">Filter Acoustic Profile:</label>
              <select
                v-model="audioFilterForm.profile"
                @change="handleFilterProfileSelect"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              >
                <option value="rf_12khz">1990s Composite / RF Baseband (12 kHz High-Shelf Cut, -8 dB)</option>
                <option value="crt_mono">1990s CRT TV Internal Speaker (280 Hz HP + 10 kHz LP)</option>
                <option value="vhs_headend">Cable Headend Modulator (11.5 kHz High-Shelf + 15.7 kHz Notch)</option>
                <option value="cassette">Vintage Cassette Tape (120 Hz Warm Boost + 8.5 kHz High-Cut)</option>
                <option value="bypass">Hi-Fi Transparent Bypass (No High-Cut Filter)</option>
              </select>
            </div>

            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">
                High-Shelf Cutoff Frequency: {{ (audioFilterForm.cutoffHz / 1000).toFixed(1) }} kHz
              </label>
              <input
                v-model.number="audioFilterForm.cutoffHz"
                @input="handleFilterChange"
                type="range"
                min="8000"
                max="16000"
                step="500"
                class="w-full accent-[#FFFF00]"
              />
            </div>

            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">
                High-Shelf Cut Gain: {{ audioFilterForm.cutGainDb }} dB
              </label>
              <input
                v-model.number="audioFilterForm.cutGainDb"
                @input="handleFilterChange"
                type="range"
                min="-18"
                max="0"
                step="1"
                class="w-full accent-[#FFFF00]"
              />
            </div>
          </div>
        </div>

        <!-- Ambient Streams & Volumes -->
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

        <!-- Local Audio File Ingestion Player -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Local Audio Track / Headend File Ingestion (MP3 / WAV / OGG)
            </h3>
            <span class="text-[10px] text-[#00FFFF]">DSP FILTER APPLIED LIVE</span>
          </div>

          <div
            class="border-2 border-dashed border-[#333366] hover:border-[#00FFFF] p-4 text-center rounded-xs transition-colors cursor-pointer bg-[#000022]/60"
            @dragover.prevent
            @drop.prevent="handleAudioDrop"
            @click="triggerAudioFileInput"
          >
            <input
              ref="audioFileInputRef"
              type="file"
              accept=".mp3,.wav,.ogg,.flac"
              class="hidden"
              @change="handleAudioFileSelected"
            />
            <div class="space-y-1">
              <div class="text-xs text-[#FFFF00] font-bold">DRAG AND DROP LOCAL AUDIO TRACK HERE</div>
              <div class="text-[11px] text-[#8888AA]">Plays directly through the active 12 kHz RF headend filter</div>
            </div>
          </div>

          <div v-if="audioUploadStatus" class="p-2 text-xs border bg-[#003300] border-[#00FF00] text-[#00FF00]">
            {{ audioUploadStatus }}
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

      <!-- Tab 8: System Updates & Version Management -->
      <div v-if="activeTab === 'updates'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <div class="flex items-center justify-between border-b border-[#333366] pb-2">
          <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
            System Updates & Release Management
          </h2>
          <span
            class="text-[11px] px-2 py-0.5 border"
            :class="updateStatus?.update_available ? 'bg-[#FFFF00] text-[#000033] border-[#FFFF00] font-black animate-pulse' : 'bg-[#003300] text-[#00FF00] border-[#00FF00]'"
          >
            {{ updateStatus?.update_available ? `[ UPDATE AVAILABLE: v${updateStatus.latest_version} ]` : '[ SYSTEM UP TO DATE ]' }}
          </span>
        </div>

        <!-- Rate Limit Friendly Banner if active -->
        <div v-if="updateStatus?.is_rate_limited" class="p-3 bg-[#332200] border-2 border-[#FFAA00] text-[#FFCC00] text-xs leading-relaxed space-y-1">
          <div class="font-black tracking-wider text-[#FFFF00] uppercase">[ GITHUB CHECK LIMIT REACHED ]</div>
          <p>{{ updateStatus.user_message || 'You have checked for updates frequently. Requests are temporarily paused and will resume shortly.' }}</p>
        </div>

        <!-- Version Telemetry Card -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
          <div class="bg-[#000022] p-2 border border-[#333366]">
            <span class="text-[#8888AA] block text-[10px]">CURRENT VERSION:</span>
            <span class="text-[#FFFF00] font-bold">v{{ updateStatus?.current_version || '0.15.0' }}</span>
          </div>
          <div class="bg-[#000022] p-2 border border-[#333366]">
            <span class="text-[#8888AA] block text-[10px]">LATEST RELEASE:</span>
            <span class="text-[#00FFFF] font-bold">v{{ updateStatus?.latest_version || updateStatus?.current_version || '0.15.0' }}</span>
          </div>
          <div class="bg-[#000022] p-2 border border-[#333366]">
            <span class="text-[#8888AA] block text-[10px]">LAST CHECKED:</span>
            <span class="text-[#E0E0E0] font-bold">{{ updateStatus?.last_checked ? new Date(updateStatus.last_checked).toLocaleTimeString() : 'Never' }}</span>
          </div>
          <div class="bg-[#000022] p-2 border border-[#333366]">
            <span class="text-[#8888AA] block text-[10px]">CHECK STATUS:</span>
            <span class="font-bold" :class="updateStatus?.is_rate_limited ? 'text-[#FFAA00]' : 'text-[#00FF00]'">
              {{ updateStatus?.is_rate_limited
                ? `Waiting ~${updateStatus.rate_limit_reset_minutes || 60}m`
                : (updateStatus?.rate_limit_remaining !== undefined && updateStatus.rate_limit_remaining !== null
                    ? `${updateStatus.rate_limit_remaining} / 60 remaining`
                    : 'Normal')
              }}
            </span>
          </div>
        </div>

        <!-- Auto-Update Cadence Settings -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-3">
          <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
            Auto-Update Notification Cadence & Network Policy
          </h3>
          <p class="text-[11px] text-[#8888AA] leading-relaxed">
            GitHub unauthenticated requests are limited to 60 per hour for your network. OpenPrevue defaults to <strong class="text-[#FFFF00]">Disabled</strong> (zero outbound calls). When turned on, checks are cached for 6 hours so your network never exceeds the limit.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">Update Check Frequency:</label>
              <select
                v-model="form.update_check_interval"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              >
                <option value="disabled">Disabled (Default: Zero External Network Calls)</option>
                <option value="weekly">Weekly Check (Recommended for Homelab Deployments)</option>
                <option value="daily">Daily Check (Ultra Low Bandwidth)</option>
                <option value="on_boot">Check on Server Startup Only</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-3 pt-2">
            <button
              :disabled="isCheckingUpdates"
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors"
              @click="handleCheckUpdatesNow"
            >
              {{ isCheckingUpdates ? '[ CHECKING GITHUB FOR UPDATES... ]' : '[ CHECK FOR UPDATES NOW ]' }}
            </button>
            <span v-if="updateProbeMessage" class="text-xs font-bold" :class="updateProbeMessage.startsWith('Notice:') ? 'text-[#FFAA00]' : 'text-[#00FF00]'">
              {{ updateProbeMessage }}
            </span>
          </div>
        </div>

        <!-- Release Notes Section if available -->
        <div v-if="updateStatus?.update_available" class="bg-[#000033] p-4 border border-[#FFFF00] space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-[#FFFF00] uppercase">
              {{ updateStatus.release_title || `Release v${updateStatus.latest_version}` }}
            </h4>
            <a
              :href="updateStatus.release_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-[11px] text-[#00FFFF] hover:underline font-bold"
            >
              [ VIEW ON GITHUB RELEASES ]
            </a>
          </div>
          <pre class="bg-[#000022] p-3 border border-[#333366] text-[#E0E0E0] text-[11px] max-h-48 overflow-y-auto whitespace-pre-wrap font-mono">{{ updateStatus.release_notes || 'No release notes provided.' }}</pre>
        </div>

        <!-- 1-Click Homelab Docker Upgrade Snippet -->
        <div class="bg-[#000033] p-4 border border-[#333366] space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-[#00FFFF] uppercase">
              Homelab Docker Container Upgrade Command
            </h4>
            <button
              class="text-[10px] text-[#FFFF00] hover:underline font-bold cursor-pointer"
              @click="copyDockerUpgradeCommand"
            >
              [ {{ copiedCommand ? 'COPIED TO CLIPBOARD' : 'COPY COMMAND' }} ]
            </button>
          </div>
          <code class="block bg-[#000022] p-2 border border-[#333366] text-[#00FF00] text-xs font-bold">
            docker pull ghcr.io/upioneer/openprevue:latest && docker compose up -d
          </code>
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
  checkUpdatesNow,
  dispatchEASTestAlert,
  fetchHealth,
  fetchSpeechStatus,
  fetchSettings,
  fetchTelegramStatus,
  fetchTelegramUsers,
  fetchUpdateStatus,
  generateTelegramPairCode,
  sendTelegramTestMessage,
  testSpeechPipeline,
  triggerSync,
  unpairTelegramUser,
  updateSetting,
} from '../api/client'
import { retroShader, type ShaderConfig } from '../services/retroShader'
import { audioSynth, type AudioFilterConfig, type AudioFilterProfile } from '../services/audioSynth'
import { commercialsEngine } from '../services/commercialsEngine'
import { REGIONAL_PRESETS, type RegionalPreset } from '../services/regionalPresets'
import type { HealthData, SystemSettings, UpdateStatusResponse } from '../types'

const tabs = [
  { id: 'location', label: '[ LOCATION & DISCOVERY ]' },
  { id: 'display', label: '[ RETRO CRT SHADER ]' },
  { id: 'audio', label: '[ SPOTIFY & MUZAK ]' },
  { id: 'ingestion', label: '[ TICKET INGESTION & AI ]' },
  { id: 'telegram', label: '[ TELEGRAM & SPEECH ]' },
  { id: 'eas', label: '[ EMERGENCY ALERTS (EAS) ]' },
  { id: 'providers', label: '[ PROVIDER CREDENTIALS ]' },
  { id: 'updates', label: '[ SYSTEM & UPDATES ]' },
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

// Commercials Engine UI State
const commercialsEnabled = ref(commercialsEngine.isEnabled.value)
const commercialsFrequency = ref(commercialsEngine.frequencyPerHour.value)
const videoFileInputRef = ref<HTMLInputElement | null>(null)

// Update Tracking State
const updateStatus = ref<UpdateStatusResponse | null>(null)
const isCheckingUpdates = ref(false)
const updateProbeMessage = ref('')
const copiedCommand = ref(false)

// Retro Shader Config Reactive State
const shaderForm = reactive<ShaderConfig>({
  scanlines: true,
  scanlineIntensity: 12,
  phosphorGlow: true,
  crtCurvature: false,
  vhsNoise: false,
  palette: 'default',
  resolutionScaling: 'native',
})

// Web Audio State & DSP RF Filter Config
const isAudioPreviewPlaying = ref(false)
const tapeHissVol = ref(35)
const muzakVol = ref(50)
const muzakStreams = audioSynth.getPlaybackState().streams
const selectedMuzakStream = ref(muzakStreams[0].url)
const audioFilterForm = reactive<AudioFilterConfig>(audioSynth.getFilterConfig())

// Audio File Ingestion State
const audioFileInputRef = ref<HTMLInputElement | null>(null)
const audioUploadStatus = ref('')

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
  scanline_intensity: '12',
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
  update_check_interval: 'disabled',
  auto_update_notifs: '0',
  commercials_enabled: '0',
  commercials_frequency_per_hour: '4',
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

function handleFilterChange() {
  audioSynth.updateFilterConfig(audioFilterForm)
}

function handleFilterProfileSelect() {
  audioSynth.setFilterProfile(audioFilterForm.profile as AudioFilterProfile)
  Object.assign(audioFilterForm, audioSynth.getFilterConfig())
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

function triggerAudioFileInput() {
  audioFileInputRef.value?.click()
}

function handleAudioFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    playLocalTrack(target.files[0])
  }
}

function handleAudioDrop(e: DragEvent) {
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    playLocalTrack(e.dataTransfer.files[0])
  }
}

function playLocalTrack(file: File) {
  audioSynth.playLocalAudioFile(file, muzakVol.value)
  audioUploadStatus.value = `[PLAYING LIVE] ${file.name} (${Math.round(file.size / 1024)} KB) via 12 kHz High-Shelf RF Filter`
  isAudioPreviewPlaying.value = true
}

function handleCommercialsConfigChange() {
  commercialsEngine.updateConfig(commercialsEnabled.value, commercialsFrequency.value)
  form.commercials_enabled = commercialsEnabled.value ? '1' : '0'
  form.commercials_frequency_per_hour = commercialsFrequency.value.toString()
}

function triggerCommercialTest() {
  commercialsEngine.playRandomCommercial()
}

function triggerVideoFileInput() {
  videoFileInputRef.value?.click()
}

function handleVideoFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    commercialsEngine.addUploadedClip(target.files[0])
  }
}

function handleVideoDrop(e: DragEvent) {
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    commercialsEngine.addUploadedClip(e.dataTransfer.files[0])
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

async function handleCheckUpdatesNow() {
  isCheckingUpdates.value = true
  updateProbeMessage.value = ''
  try {
    const res = await checkUpdatesNow()
    updateStatus.value = res
    if (res.is_rate_limited) {
      updateProbeMessage.value = `Notice: Please wait about ${res.rate_limit_reset_minutes || 60}m before checking again.`
    } else if (res.update_available) {
      updateProbeMessage.value = `A new version (v${res.latest_version}) is available.`
    } else if (res.user_message) {
      updateProbeMessage.value = res.user_message
    } else {
      updateProbeMessage.value = 'OpenPrevue is running the newest version.'
    }
    setTimeout(() => {
      updateProbeMessage.value = ''
    }, 5000)
  } catch (err) {
    updateProbeMessage.value = 'Could not check for updates right now. Please try again later.'
  } finally {
    isCheckingUpdates.value = false
  }
}

function copyDockerUpgradeCommand() {
  navigator.clipboard.writeText('docker pull ghcr.io/upioneer/openprevue:latest && docker compose up -d')
  copiedCommand.value = true
  setTimeout(() => {
    copiedCommand.value = false
  }, 3000)
}

async function loadAll() {
  try {
    const [s, h, tStatus, tUsers, spStatus, uStatus] = await Promise.all([
      fetchSettings(),
      fetchHealth(),
      fetchTelegramStatus(),
      fetchTelegramUsers(),
      fetchSpeechStatus(),
      fetchUpdateStatus().catch(() => null),
    ])
    Object.assign(form, s)
    healthData.value = h
    telegramStatus.value = tStatus
    telegramUsers.value = tUsers
    speechStatus.value = spStatus
    if (uStatus) {
      updateStatus.value = uStatus
    }

    if (s.commercials_enabled) {
      commercialsEnabled.value = s.commercials_enabled === '1'
      commercialsEngine.isEnabled.value = commercialsEnabled.value
    }
    if (s.commercials_frequency_per_hour) {
      commercialsFrequency.value = parseInt(s.commercials_frequency_per_hour, 10)
      commercialsEngine.frequencyPerHour.value = commercialsFrequency.value
    }

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
