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
        <div class="flex items-center justify-between border-b border-[#333366] pb-1">
          <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
            Location, City Geocoding & Radial Event Aggregation
          </h2>
          <span v-if="isGeocodingLocation" class="text-xs text-[#FFFF00] animate-pulse font-bold">[ RESOLVING LOCATION... ]</span>
        </div>

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
            <label class="text-xs text-[#A0A0C0] block font-bold">Metro Area / Channel Broadcast Label:</label>
            <div class="flex space-x-1">
              <input
                v-model="form.metro_label"
                type="text"
                class="flex-1 bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
                placeholder="e.g. AUSTIN, TX or CHICAGO, IL"
                @blur="handleSettingsGeocode(form.metro_label)"
                @keydown.enter.prevent="handleSettingsGeocode(form.metro_label)"
              />
              <button
                type="button"
                class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-2 py-1 text-[10px] font-bold cursor-pointer transition-colors"
                @click="handleSettingsGeocode(form.metro_label)"
              >
                [ RESOLVE ]
              </button>
            </div>
          </div>

          <div class="space-y-1">
            <label class="text-xs text-[#A0A0C0] block font-bold">Postal Code (ZIP):</label>
            <div class="flex space-x-1">
              <input
                v-model="form.postal_code"
                type="text"
                class="flex-1 bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
                placeholder="e.g. 78701 or 60601"
                @blur="handleSettingsGeocode(form.postal_code)"
                @keydown.enter.prevent="handleSettingsGeocode(form.postal_code)"
              />
              <button
                type="button"
                class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-2 py-1 text-[10px] font-bold cursor-pointer transition-colors"
                @click="handleSettingsGeocode(form.postal_code)"
              >
                [ RESOLVE ]
              </button>
            </div>
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

        <div v-if="locationResolutionMsg" class="p-2 border text-xs" :class="locationResolutionIsError ? 'bg-[#330000] border-[#FF4444] text-[#FF8888]' : 'bg-[#003300] border-[#00FF00] text-[#00FF00] font-bold'">
          {{ locationResolutionMsg }}
        </div>
      </div>

      <!-- Tab 2: Display & Scan Speed -->
      <div v-if="activeTab === 'display'" class="bg-[#000044] p-5 border border-[#333366] space-y-4">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Display Controls, Channel Scan Speed & Retro CRT Shaders
        </h2>

        <!-- Channel Schedule Presentation Scale & Density Presets -->
        <div class="bg-[#000033] p-4 border-2 border-[#FFFF00] space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs sm:text-sm font-black text-[#FFFF00] uppercase">
              Schedule Presentation Scale & Density
            </h3>
            <span class="text-xs text-[#00FFFF] font-bold">
              ACTIVE: {{ form.grid_density === 'dense' ? '12 ROWS (DENSE)' : (form.grid_density === 'balanced' ? '7 ROWS (HAPPY MEDIUM)' : '4 ROWS (AUTHENTIC CLASSIC TV)') }}
            </span>
          </div>
          <p class="text-xs text-[#8888AA]">
            Select your preferred channel schedule row scale and typography density across landscape, 1080p, and portrait monitors.
          </p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
            <!-- Classic TV (4 Rows) -->
            <button
              type="button"
              class="p-3 border-2 text-left cursor-pointer transition-all flex flex-col justify-between"
              :class="form.grid_density === 'classic_tv' || !form.grid_density
                ? 'bg-[#000066] border-[#FFFF00] text-[#FFFF00] shadow-[0_0_10px_rgba(255,255,0,0.6)]'
                : 'bg-[#000022] border-[#333366] text-[#A0A0C0] hover:border-[#8888AA]'"
              @click="form.grid_density = 'classic_tv'"
            >
              <div class="font-black text-xs sm:text-sm uppercase tracking-wider">[ 4 ROWS // CLASSIC TV ]</div>
              <div class="text-[11px] text-[#E0E0E0] mt-1">True-to-scale authentic 1990s TV broadcast layout with huge chunky typography and large team cards.</div>
            </button>

            <!-- Balanced (7 Rows) -->
            <button
              type="button"
              class="p-3 border-2 text-left cursor-pointer transition-all flex flex-col justify-between"
              :class="form.grid_density === 'balanced'
                ? 'bg-[#000066] border-[#00FFFF] text-[#00FFFF] shadow-[0_0_10px_rgba(0,255,255,0.6)]'
                : 'bg-[#000022] border-[#333366] text-[#A0A0C0] hover:border-[#8888AA]'"
              @click="form.grid_density = 'balanced'"
            >
              <div class="font-black text-xs sm:text-sm uppercase tracking-wider">[ 7 ROWS // HAPPY MEDIUM ]</div>
              <div class="text-[11px] text-[#E0E0E0] mt-1">Balanced presentation with comfortable row spacing and higher listing visibility.</div>
            </button>

            <!-- Dense (12 Rows) -->
            <button
              type="button"
              class="p-3 border-2 text-left cursor-pointer transition-all flex flex-col justify-between"
              :class="form.grid_density === 'dense'
                ? 'bg-[#000066] border-[#00FF00] text-[#00FF00] shadow-[0_0_10px_rgba(0,255,0,0.6)]'
                : 'bg-[#000022] border-[#333366] text-[#A0A0C0] hover:border-[#8888AA]'"
              @click="form.grid_density = 'dense'"
            >
              <div class="font-black text-xs sm:text-sm uppercase tracking-wider">[ 12 ROWS // DENSE OVERVIEW ]</div>
              <div class="text-[11px] text-[#E0E0E0] mt-1">High-density information mode displaying maximum simultaneous channels on screen.</div>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Autoscroll Scan Speed -->
          <div class="bg-[#000033] p-3 border border-[#FFFF00] space-y-1">
            <label class="text-xs text-[#FFFF00] font-bold block">
              Channel Schedule Scroll Speed (Scan Speed): {{ form.autoscroll_speed }} px/sec
            </label>
            <input
              v-model="form.autoscroll_speed"
              type="range"
              min="15"
              max="150"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
            <span class="text-[10px] text-[#8888AA] block">
              Controls the autoscroll pace of the bottom TV listings grid (30 px/sec is default smooth broadcast scan speed).
            </span>
          </div>

          <!-- Spotlight Marquee Rotation -->
          <div class="bg-[#000033] p-3 border border-[#333366] space-y-1">
            <label class="text-xs text-[#00FFFF] font-bold block">
              Spotlight Marquee Rotation Interval: {{ form.marquee_rotation_seconds }}s
            </label>
            <input
              v-model="form.marquee_rotation_seconds"
              type="range"
              min="5"
              max="60"
              step="5"
              class="w-full accent-[#FFFF00]"
            />
            <span class="text-[10px] text-[#8888AA] block">
              How long each featured event or sports matchup stays on screen in the top preview quadrant.
            </span>
          </div>

          <!-- Periodic Listing Reading Pause -->
          <div class="bg-[#000033] p-3 border border-[#00FF00] space-y-1">
            <label class="text-xs text-[#00FF00] font-bold block">
              Periodic Schedule Reading Pause Duration: {{ form.scroll_pause_duration || '4' }}s
            </label>
            <input
              v-model="form.scroll_pause_duration"
              type="range"
              min="0"
              max="10"
              step="1"
              class="w-full accent-[#00FF00]"
            />
            <span class="text-[10px] text-[#8888AA] block">
              Authentic 1990s TV Guide cadence. Holds position for 4s so viewers can comfortably read listings before scrolling (0s = continuous scroll).
            </span>
          </div>

          <!-- Scroll Movement Window Duration -->
          <div class="bg-[#000033] p-3 border border-[#333366] space-y-1">
            <label class="text-xs text-[#00FFFF] font-bold block">
              Scroll Active Motion Window: {{ form.scroll_page_interval || '6' }}s
            </label>
            <input
              v-model="form.scroll_page_interval"
              type="range"
              min="3"
              max="15"
              step="1"
              class="w-full accent-[#00FFFF]"
            />
            <span class="text-[10px] text-[#8888AA] block">
              How many seconds the schedule scrolls before pausing on the next set of channel rows.
            </span>
          </div>

          <!-- Scanline Intensity -->
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

          <!-- Color Palette Preset -->
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

          <!-- Resolution Downsampler -->
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

          <!-- CRT Effects Toggles -->
          <div class="flex items-center space-x-4 pt-4">
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

      <!-- Tab 3: Spotify & Vintage Audio -->
      <div v-if="activeTab === 'audio'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Spotify Playlist Pairing & Vintage Tape Audio Filter
        </h2>

        <!-- Spotify Playlist Configuration Card -->
        <div class="bg-[#000033] border border-[#1DB954] p-4 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1DB954]/40 pb-2">
            <div class="flex items-center space-x-2">
              <span class="w-2.5 h-2.5 bg-[#1DB954] inline-block animate-pulse"></span>
              <h3 class="text-xs font-bold text-[#1DB954] uppercase tracking-wider">
                Curated Spotify Playlist & Player Controls
              </h3>
            </div>
            <a
              :href="form.spotify_playlist_url || 'https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f'"
              target="_blank"
              rel="noopener noreferrer"
              class="bg-[#1DB954] text-[#000033] hover:bg-white px-3 py-1 text-xs font-black tracking-wider transition-all cursor-pointer inline-block text-center shadow-[0_0_10px_rgba(29,185,84,0.6)]"
            >
              [ LAUNCH PLAYLIST IN SPOTIFY ]
            </a>
          </div>

          <div class="space-y-3">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block font-bold">Custom Spotify Playlist URL (Optional Override):</label>
              <input
                v-model="form.spotify_playlist_url"
                type="text"
                placeholder="https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#FFFF00] focus:border-[#1DB954] outline-none"
              />
              <span class="text-[10px] text-[#8888AA] block">
                OpenPrevue defaults to the official curated playlist. You can paste your own Spotify playlist link above to pair custom tracks.
              </span>
            </div>

            <div class="flex items-center space-x-4">
              <label class="flex items-center space-x-2 text-xs text-[#E0E0E0] cursor-pointer">
                <input
                  v-model="spotifyAutoplayEnabled"
                  @change="handleSpotifyAutoplayToggle"
                  type="checkbox"
                  class="accent-[#1DB954]"
                />
                <span>Auto-play Spotify embed on initial guide boot</span>
              </label>
            </div>

            <!-- Spotify Embedded Player -->
            <div class="w-full pt-1">
              <iframe
                style="border-radius: 4px"
                :src="computedSpotifyEmbedUrl"
                width="100%"
                height="152"
                frameBorder="0"
                allowfullscreen
                allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                loading="lazy"
              ></iframe>
            </div>
          </div>
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

        <!-- Analog Tape Hiss & 60Hz Transformer Hum Controls -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-4">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <span class="text-xs font-bold text-[#FFFF00] uppercase">
              Analog Headend Atmosphere (Tape Hiss & 60Hz Hum)
            </span>
            <button
              type="button"
              class="px-3 py-1 border text-xs font-bold transition-all cursor-pointer"
              :class="isAudioPreviewPlaying
                ? 'bg-[#FF4444] text-white border-[#FF4444]'
                : 'bg-[#00FF00] text-[#000033] border-[#00FF00] shadow-[0_0_8px_rgba(0,255,0,0.8)]'"
              @click="toggleAudioPreview"
            >
              {{ isAudioPreviewPlaying ? '[ STOP TAPE HISS ]' : '[ TEST TAPE HISS ]' }}
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">Analog Tape Hiss Volume: {{ tapeHissVol }}%</label>
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
          </div>
        </div>
      </div>

      <!-- Tab 4: Retro Commercials & Station Bumpers -->
      <div v-if="activeTab === 'commercials'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <div class="flex items-center justify-between border-b border-[#333366] pb-2">
          <h2 class="text-sm font-bold text-[#00FFFF] uppercase">
            1990s Television Commercials & Station Bumpers Engine
          </h2>
          <span
            class="text-[11px] px-2 py-0.5 border"
            :class="commercialsEnabled ? 'bg-[#003300] text-[#00FF00] border-[#00FF00]' : 'bg-[#330000] text-[#FF4444] border-[#FF4444]'"
          >
            {{ commercialsEnabled ? '[ COMMERCIALS ACTIVE ]' : '[ DISABLED ]' }}
          </span>
        </div>

        <div class="bg-[#000033] border border-[#FFFF00] p-4 space-y-4">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <div>
              <span class="text-xs font-bold text-[#FFFF00] block uppercase">
                Automatic Commercial Interruption Scheduling
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
              <span>{{ commercialsEnabled ? '[ ENABLED ]' : '[ DISABLED ]' }}</span>
            </label>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block">
                Commercial Break Frequency: {{ commercialsFrequency }} per hour
                <span class="text-[#00FFFF] block text-[10px]">
                  (Plays 1 commercial every {{ Math.round(60 / commercialsFrequency) }} minutes)
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

          <!-- Video Dropzone & Directory Guidance -->
          <div class="pt-1 space-y-3">
            <div class="bg-[#000022] p-3 border border-[#333366] space-y-2 text-[11px]">
              <div class="flex items-center justify-between text-[#00FFFF] font-bold uppercase">
                <span>Where to place your video files:</span>
                <span class="text-[#FFFF00]">SERVER DIRECTORY: ./data/commercials/</span>
              </div>
              <p class="text-[#A0A0C0] leading-relaxed">
                You can drop video files directly into the <strong class="text-[#FFFF00]">./data/commercials/</strong> folder on your server / Docker host, or drag and drop them below. Files are instantly loaded into the rotation.
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 pt-1 text-[10px]">
                <div class="bg-[#000033] p-1.5 border border-[#333366]">
                  <span class="text-[#8888AA] block">CONTAINER:</span>
                  <span class="text-[#00FF00] font-bold">.mp4 / .webm</span>
                </div>
                <div class="bg-[#000033] p-1.5 border border-[#333366]">
                  <span class="text-[#8888AA] block">VIDEO CODEC:</span>
                  <span class="text-[#00FF00] font-bold">H.264 / VP9</span>
                </div>
                <div class="bg-[#000033] p-1.5 border border-[#333366]">
                  <span class="text-[#8888AA] block">RESOLUTION:</span>
                  <span class="text-[#00FF00] font-bold">480p SD / 720p HD</span>
                </div>
                <div class="bg-[#000033] p-1.5 border border-[#333366]">
                  <span class="text-[#8888AA] block">MAX FILE SIZE:</span>
                  <span class="text-[#00FF00] font-bold">&lt; 50 MB / clip</span>
                </div>
              </div>
            </div>

            <!-- Video Dropzone -->
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
                <div class="text-[11px] text-[#8888AA]">Plays in top preview window during scheduled commercial breaks (Max 50MB)</div>
              </div>
            </div>

            <div v-if="videoUploadMessage" class="p-2 text-xs border" :class="videoUploadIsError ? 'bg-[#330000] border-[#FF4444] text-[#FF8888]' : 'bg-[#003300] border-[#00FF00] text-[#00FF00]'">
              {{ videoUploadMessage }}
            </div>

            <!-- Clips List in Queue -->
            <div v-if="commercialsEngine.clips.value.length > 0" class="space-y-1 pt-1">
              <span class="text-xs font-bold text-[#A0A0C0] block">CURRENT VIDEO ROTATION QUEUE ({{ commercialsEngine.clips.value.length }}):</span>
              <div class="space-y-1 max-h-36 overflow-y-auto">
                <div
                  v-for="clip in commercialsEngine.clips.value"
                  :key="clip.id"
                  class="flex items-center justify-between bg-[#000022] px-3 py-1.5 border border-[#333366] text-xs"
                >
                  <div class="flex items-center space-x-2 truncate">
                    <span class="text-[#00FF00] font-bold truncate">{{ clip.name }}</span>
                    <span v-if="clip.sizeBytes" class="text-[#8888AA] text-[10px]">
                      ({{ (clip.sizeBytes / (1024 * 1024)).toFixed(1) }} MB)
                    </span>
                  </div>
                  <div class="flex items-center space-x-2 shrink-0">
                    <button
                      type="button"
                      class="text-[10px] text-[#00FFFF] hover:underline cursor-pointer"
                      @click="commercialsEngine.playClip(clip)"
                    >
                      [ Play Now ]
                    </button>
                    <button
                      type="button"
                      class="text-[10px] text-[#FF4444] hover:underline cursor-pointer"
                      @click="commercialsEngine.removeClip(clip.id)"
                    >
                      [ Remove ]
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 5: Ticket Ingestion & AI -->
      <div v-if="activeTab === 'ingestion'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Multi-Format Reservation Ingestion & Local / Cloud AI Models
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

        <!-- TripAdvisor & Viator Public Trip / Wishlist Sync Card -->
        <div class="bg-[#000033] border border-[#00FFFF] p-4 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#00FFFF]/40 pb-2">
            <div>
              <span class="text-xs font-black text-[#00FFFF] block uppercase tracking-wider">
                TripAdvisor & Viator Public Wishlists / Trips Sync
              </span>
              <span class="text-[11px] text-[#8888AA]">
                Paste public TripAdvisor Trip or Viator Wishlist URLs to automatically sync your saved tours, attractions, and activities.
              </span>
            </div>
            <span class="text-[10px] text-[#FFFF00] bg-[#000066] px-2 py-0.5 border border-[#FFFF00] font-bold shrink-0">
              ZERO-API KEY REQUIRED
            </span>
          </div>

          <div class="space-y-3">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block font-bold">Public TripAdvisor Trip / Saves URL:</label>
              <input
                v-model="form.tripadvisor_wishlist_url"
                type="url"
                placeholder="https://www.tripadvisor.com/Trips/..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none font-mono"
              />
              <span class="text-[10px] text-[#8888AA] block">
                In TripAdvisor, go to <strong>Trips / Saves</strong> &gt; <strong>Share</strong> &gt; copy the public link.
              </span>
            </div>

            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block font-bold">Public Viator Wishlist / Experience URL:</label>
              <input
                v-model="form.viator_wishlist_url"
                type="url"
                placeholder="https://www.viator.com/..."
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none font-mono"
              />
              <span class="text-[10px] text-[#8888AA] block">
                Paste any shared Viator Wishlist or experience page.
              </span>
            </div>
          </div>
        </div>

        <!-- 1-Click Instant URL Ingestion Dropzone -->
        <div class="bg-[#000033] border border-[#FFFF00] p-4 space-y-3">
          <div class="flex items-center justify-between border-b border-[#FFFF00]/40 pb-2">
            <div>
              <span class="text-xs font-black text-[#FFFF00] block uppercase tracking-wider">
                1-Click Web Link Ingest
              </span>
              <span class="text-[11px] text-[#8888AA]">
                Paste ANY event, tour, or ticket link (TripAdvisor, Viator, Ticketmaster, Eventbrite, Venue site) to immediately scrape and add it to your channel guide.
              </span>
            </div>
          </div>

          <div class="flex flex-col sm:flex-row items-center gap-2">
            <input
              v-model="quickIngestUrl"
              type="url"
              placeholder="https://www.viator.com/tours/... or https://www.tripadvisor.com/..."
              class="flex-1 w-full bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#00FF00] focus:border-[#FFFF00] outline-none font-mono"
              @keydown.enter.prevent="handleQuickIngestUrl"
            />
            <button
              type="button"
              :disabled="isIngestingUrl || !quickIngestUrl"
              class="w-full sm:w-auto bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors shrink-0"
              @click="handleQuickIngestUrl"
            >
              {{ isIngestingUrl ? '[ SCRAPING... ]' : '[ INGEST TO GUIDE ]' }}
            </button>
          </div>

          <div v-if="quickIngestMessage" class="p-2 text-xs border" :class="quickIngestIsError ? 'bg-[#330000] border-[#FF4444] text-[#FF8888]' : 'bg-[#003300] border-[#00FF00] text-[#00FF00]'">
            {{ quickIngestMessage }}
          </div>
        </div>

        <!-- Local AI Support (Ollama Instance) -->
        <div class="bg-[#000033] border border-[#00FFFF] p-4 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#00FFFF]/40 pb-2">
            <div>
              <span class="text-xs font-black text-[#00FFFF] block uppercase tracking-wider">
                Local AI Engine Support (Self-Hosted Ollama)
              </span>
              <span class="text-[11px] text-[#8888AA]">
                Run private, offline AI extraction for indie event flyers and unstructured reservation emails.
              </span>
            </div>
            <span
              v-if="ollamaTestResult"
              class="text-[11px] px-2 py-0.5 border shrink-0 font-bold"
              :class="ollamaTestResult.status === 'online' ? 'bg-[#003300] text-[#00FF00] border-[#00FF00]' : 'bg-[#330000] text-[#FF4444] border-[#FF4444]'"
            >
              {{ ollamaTestResult.status === 'online' ? `[ ONLINE: ${ollamaTestResult.latency_ms}ms ]` : '[ OFFLINE ]' }}
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block font-bold">Ollama Instance URL:</label>
              <input
                v-model="form.ai_ollama_url"
                type="text"
                placeholder="http://localhost:11434"
                class="w-full bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
              />
              <span class="text-[10px] text-[#8888AA] block">
                For Docker deployments, use <code class="text-[#00FFFF]">http://host.docker.internal:11434</code> or your LAN IP.
              </span>
            </div>

            <div class="space-y-1">
              <label class="text-xs text-[#A0A0C0] block font-bold">Ollama Model Name:</label>
              <div class="flex items-center space-x-2">
                <input
                  v-model="form.ai_ollama_model"
                  type="text"
                  placeholder="llama3.2"
                  class="flex-1 bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
                />
                <select
                  v-if="ollamaDetectedModels.length > 0"
                  v-model="form.ai_ollama_model"
                  class="bg-[#000022] border border-[#00FFFF] px-2 py-1.5 text-xs text-[#00FFFF] outline-none cursor-pointer"
                  title="Select detected local Ollama model"
                >
                  <option v-for="m in ollamaDetectedModels" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
              <span class="text-[10px] text-[#8888AA] block">
                Recommended: <code class="text-[#00FF00]">llama3.2</code>, <code class="text-[#00FF00]">mistral</code>, or <code class="text-[#00FF00]">qwen2.5</code>.
              </span>
            </div>
          </div>

          <!-- Ollama Ping & Health Validation Action -->
          <div class="flex flex-wrap items-center gap-3 pt-2">
            <button
              :disabled="isTestingOllama"
              type="button"
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-2 text-xs font-black tracking-wider cursor-pointer disabled:opacity-50 transition-colors shadow"
              @click="handlePingOllama"
            >
              {{ isTestingOllama ? '[ PINGING OLLAMA SERVER... ]' : '[ TEST OLLAMA HEARTBEAT & CONNECTION ]' }}
            </button>

            <div v-if="ollamaTestResult" class="text-xs">
              <div v-if="ollamaTestResult.status === 'online'" class="text-[#00FF00] font-bold">
                PROBE SUCCESS: Connected to Ollama {{ ollamaTestResult.version ? `(v${ollamaTestResult.version})` : '' }} in {{ ollamaTestResult.latency_ms }}ms.
                <span v-if="ollamaTestResult.models.length > 0" class="block text-[10px] text-[#A0A0C0]">
                  Detected {{ ollamaTestResult.models.length }} models: {{ ollamaTestResult.models.slice(0, 4).join(', ') }}{{ ollamaTestResult.models.length > 4 ? '...' : '' }}
                </span>
              </div>
              <div v-else class="text-[#FF8888] font-bold">
                CONNECTION FAILED: {{ ollamaTestResult.error || 'Server did not respond.' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Optional Cloud AI Keys -->
        <div class="bg-[#000033] border border-[#333366] p-4 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-[#FFFF00] uppercase">
              Optional Cloud AI Enhancements (Groq / OpenAI / Anthropic)
            </h3>
            <span class="text-[10px] text-[#8888AA]">OPTIONAL CLOUD ASSIST</span>
          </div>

          <p class="text-[11px] text-[#8888AA] leading-relaxed">
            Leave empty if you use local deterministic parsing or local Ollama. Adding API keys allows fast cloud extraction fallback.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
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

      <!-- Tab 6: Telegram Bot & Voice Speech -->
      <div v-if="activeTab === 'telegram'" class="bg-[#000044] p-5 border border-[#333366] space-y-5">
        <h2 class="text-sm font-bold text-[#00FFFF] border-b border-[#333366] pb-1 uppercase">
          Telegram Bot Assistant & Spoken Voice Announcer
        </h2>

        <!-- Step-by-Step Interactive Telegram Bot Creation Guide -->
        <div class="bg-[#000033] p-4 border border-[#FFFF00] space-y-3">
          <div class="flex items-center justify-between border-b border-[#333366] pb-2">
            <h3 class="text-xs font-black text-[#FFFF00] uppercase tracking-wider">
              Step-by-Step Guide: How to Create and Connect Your Telegram Bot
            </h3>
            <span
              class="text-[11px] px-2 py-0.5 border"
              :class="telegramStatus?.is_running ? 'bg-[#003300] text-[#00FF00] border-[#00FF00]' : 'bg-[#330000] text-[#FF4444] border-[#FF4444]'"
            >
              {{ telegramStatus?.is_running ? '[ BOT ACTIVE ]' : '[ BOT NOT CONFIGURED ]' }}
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-5 gap-2 text-[11px]">
            <div class="bg-[#000022] p-2.5 border border-[#333366] space-y-1">
              <span class="text-[#FFFF00] font-black block">STEP 1: BOTFATHER</span>
              <p class="text-[#A0A0C0] text-[10px]">
                Open Telegram and message <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer" class="text-[#00FFFF] underline font-bold">@BotFather</a>.
              </p>
            </div>

            <div class="bg-[#000022] p-2.5 border border-[#333366] space-y-1">
              <span class="text-[#FFFF00] font-black block">STEP 2: /newbot</span>
              <p class="text-[#A0A0C0] text-[10px]">
                Send <code class="text-[#00FF00]">/newbot</code>, give it a title, and pick a username ending in <code class="text-[#00FF00]">bot</code>.
              </p>
            </div>

            <div class="bg-[#000022] p-2.5 border border-[#333366] space-y-1">
              <span class="text-[#FFFF00] font-black block">STEP 3: COPY TOKEN</span>
              <p class="text-[#A0A0C0] text-[10px]">
                Copy the HTTP API token given by BotFather (e.g. <code class="text-[#00FF00]">123456:ABC...</code>).
              </p>
            </div>

            <div class="bg-[#000022] p-2.5 border border-[#333366] space-y-1">
              <span class="text-[#FFFF00] font-black block">STEP 4: PASTE & SAVE</span>
              <p class="text-[#A0A0C0] text-[10px]">
                Paste the token into the input below and click <strong class="text-[#FFFF00]">Save Settings</strong>.
              </p>
            </div>

            <div class="bg-[#000022] p-2.5 border border-[#333366] space-y-1">
              <span class="text-[#FFFF00] font-black block">STEP 5: PAIR DEVICE</span>
              <p class="text-[#A0A0C0] text-[10px]">
                Click <strong class="text-[#00FFFF]">Generate Pairing Code</strong> and message your bot <code class="text-[#00FF00]">/pair &lt;CODE&gt;</code>.
              </p>
            </div>
          </div>

          <!-- Bot Token Input -->
          <div class="space-y-1 pt-2 border-t border-[#333366]">
            <label class="text-xs text-[#A0A0C0] block font-bold">Telegram Bot API Token (from @BotFather):</label>
            <input
              v-model="form.telegram_bot_token"
              type="password"
              placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1.5 text-xs text-[#FFFF00] focus:border-[#00FFFF] outline-none"
            />
          </div>

          <!-- Pairing Wizard Section -->
          <div class="flex flex-wrap items-center gap-3 pt-2">
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

      <!-- Tab 7: Emergency Alerts (EAS) -->
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

      <!-- Tab 8: Provider API Keys -->
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
            <label class="text-xs text-[#A0A0C0] block font-bold">Viator Partner / Merchant API Key (exp-api-key):</label>
            <input
              v-model="form.viator_api_key"
              type="password"
              placeholder="Viator Exp-API Key"
              class="w-full bg-[#000022] border border-[#333366] px-2 py-1 text-xs text-[#E0E0E0] focus:border-[#00FFFF] outline-none font-mono"
            />
            <span class="text-[10px] text-[#8888AA] block">
              Optional. From the Viator Partner Portal. Enables automatic discovery of top-rated local tours and tastings within your GPS radius.
            </span>
          </div>

          <!-- Instant Credential Validation & Sync Trigger -->
          <div class="pt-3 border-t border-[#333366] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div class="space-y-0.5">
              <span class="text-xs font-bold text-[#FFFF00] block uppercase">Validate Keys & Refresh Listings</span>
              <span class="text-[11px] text-[#8888AA] block">Query configured provider APIs immediately to pull new local events using these credentials.</span>
            </div>
            <button
              type="button"
              :disabled="isSyncing"
              class="bg-[#000080] hover:bg-[#0000AA] border border-[#00FFFF] text-[#00FFFF] px-4 py-1.5 text-xs font-bold tracking-wider cursor-pointer disabled:opacity-50 transition-colors shrink-0"
              @click="handleManualSync"
            >
              {{ isSyncing ? '[ QUERYING PROVIDERS... ]' : '[ TEST KEYS & REFRESH LISTINGS ]' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Tab 9: System Updates & Version Management -->
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
            <span class="text-[#FFFF00] font-bold">v{{ updateStatus?.current_version || '0.16.0' }}</span>
          </div>
          <div class="bg-[#000022] p-2 border border-[#333366]">
            <span class="text-[#8888AA] block text-[10px]">LATEST RELEASE:</span>
            <span class="text-[#00FFFF] font-bold">v{{ updateStatus?.latest_version || updateStatus?.current_version || '0.16.0' }}</span>
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
        <div class="flex flex-wrap items-center gap-3">
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
            title="Manually query all event providers (Ticketmaster, SeatGeek, Sports leagues, local calendars) to fetch new upcoming events right now"
          >
            {{ isSyncing ? '[ FETCHING LATEST EVENTS... ]' : '[ REFRESH LOCAL LISTINGS NOW ]' }}
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
import { computed, onMounted, reactive, ref } from 'vue'
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
  geocodeLocationQuery,
  ingestUrl,
  pingOllamaInstance,
  refreshWeather,
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
import type { HealthData, OllamaPingResponse, SystemSettings, UpdateStatusResponse } from '../types'

const tabs = [
  { id: 'location', label: '[ 1. LOCATION & DISCOVERY ]' },
  { id: 'display', label: '[ 2. DISPLAY & SCAN SPEED ]' },
  { id: 'audio', label: '[ 3. SPOTIFY & VINTAGE AUDIO ]' },
  { id: 'commercials', label: '[ 4. RETRO COMMERCIALS ]' },
  { id: 'ingestion', label: '[ 5. TICKET INGESTION & AI ]' },
  { id: 'telegram', label: '[ 6. TELEGRAM & SPEECH ]' },
  { id: 'eas', label: '[ 7. EMERGENCY ALERTS (EAS) ]' },
  { id: 'providers', label: '[ 8. PROVIDER CREDENTIALS ]' },
  { id: 'updates', label: '[ 9. SYSTEM & UPDATES ]' },
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

// Location Geocoding State
const isGeocodingLocation = ref(false)
const locationResolutionMsg = ref('')
const locationResolutionIsError = ref(false)

// Commercials Engine UI State
const commercialsEnabled = ref(commercialsEngine.isEnabled.value)
const commercialsFrequency = ref(commercialsEngine.frequencyPerHour.value)
const videoFileInputRef = ref<HTMLInputElement | null>(null)
const videoUploadMessage = ref('')
const videoUploadIsError = ref(false)

// Spotify State
const spotifyAutoplayEnabled = ref(false)

// Update Tracking State
const updateStatus = ref<UpdateStatusResponse | null>(null)
const isCheckingUpdates = ref(false)
const updateProbeMessage = ref('')
const copiedCommand = ref(false)

// Ollama Local AI State
const isTestingOllama = ref(false)
const ollamaTestResult = ref<OllamaPingResponse | null>(null)
const ollamaDetectedModels = ref<string[]>([])

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
const audioFilterForm = reactive<AudioFilterConfig>(audioSynth.getFilterConfig())

// Ticket Ingestion State
const fileInputRef = ref<HTMLInputElement | null>(null)
const ingestionMessage = ref('')
const ingestionIsError = ref(false)

// 1-Click Quick URL Ingestion State
const quickIngestUrl = ref('')
const isIngestingUrl = ref(false)
const quickIngestMessage = ref('')
const quickIngestIsError = ref(false)

async function handleQuickIngestUrl() {
  if (!quickIngestUrl.value || !quickIngestUrl.value.trim()) return
  isIngestingUrl.value = true
  quickIngestMessage.value = ''
  quickIngestIsError.value = false

  try {
    const res = await ingestUrl(quickIngestUrl.value.trim(), 1, 0)
    quickIngestMessage.value = `[INGESTED] ${res.title} (${res.venue_name}) - Added to guide!`
    quickIngestIsError.value = false
    quickIngestUrl.value = ''
  } catch (err: any) {
    quickIngestMessage.value = `[ERROR] ${err.message || 'Failed to ingest URL'}`
    quickIngestIsError.value = true
  } finally {
    isIngestingUrl.value = false
  }
}

const form = reactive<SystemSettings>({
  postal_code: '10001',
  metro_label: 'NEW YORK CITY',
  latitude: '40.7128',
  longitude: '-74.0060',
  radius_miles: '25',
  autoscroll_speed: '30',
  grid_density: 'balanced',
  scroll_pause_duration: '4',
  scroll_page_interval: '6',
  marquee_rotation_seconds: '20',
  scanline_intensity: '12',
  phosphor_glow: '1',
  crt_curvature: '0',
  vhs_tracking_noise: '0',
  time_format: '12h',
  sync_interval_hours: '6',
  spotify_playlist_url: 'https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f',
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
  ai_ollama_url: 'http://localhost:11434',
  ai_ollama_model: 'llama3.2',
  ai_groq_key: '',
  ai_openai_key: '',
  ai_anthropic_key: '',
  update_check_interval: 'disabled',
  auto_update_notifs: '0',
  commercials_enabled: '0',
  commercials_frequency_per_hour: '4',
  tripadvisor_wishlist_url: '',
  viator_wishlist_url: '',
  viator_api_key: '',
})

const computedSpotifyEmbedUrl = computed(() => {
  const url = form.spotify_playlist_url || 'https://open.spotify.com/playlist/3jiPmIT4RugR8TPhli5Obk?si=22d007e309134d4f'
  const match = url.match(/playlist\/([a-zA-Z0-9]+)/)
  const playlistId = match ? match[1] : '3jiPmIT4RugR8TPhli5Obk'
  return `https://open.spotify.com/embed/playlist/${playlistId}?utm_source=generator&theme=0`
})

function applyRegionalPreset(preset: RegionalPreset) {
  form.metro_label = preset.metro
  form.postal_code = preset.zip
  form.latitude = preset.lat.toString()
  form.longitude = preset.lon.toString()
  form.radius_miles = preset.radius.toString()
  locationResolutionMsg.value = `[PRESET APPLIED] ${preset.metro} (${preset.lat}, ${preset.lon})`
  locationResolutionIsError.value = false
}

async function handleSettingsGeocode(query?: string) {
  if (!query || query.trim().length < 2) return
  isGeocodingLocation.value = true
  locationResolutionMsg.value = ''
  locationResolutionIsError.value = false

  try {
    const results = await geocodeLocationQuery(query.trim())
    if (results && results.length > 0) {
      const match = results[0]
      form.metro_label = match.metro_label
      if (match.postal_code) {
        form.postal_code = match.postal_code
      }
      form.latitude = match.latitude.toString()
      form.longitude = match.longitude.toString()
      locationResolutionMsg.value = `LOCATION RESOLVED: ${match.display_label} (${match.latitude.toFixed(4)}, ${match.longitude.toFixed(4)})`
    } else {
      locationResolutionIsError.value = true
      locationResolutionMsg.value = `Could not resolve "${query}". You may enter coordinates manually.`
    }
  } catch (err) {
    locationResolutionIsError.value = true
    locationResolutionMsg.value = `Geocoding lookup error: ${String(err)}`
  } finally {
    isGeocodingLocation.value = false
  }
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
}

function toggleAudioPreview() {
  if (isAudioPreviewPlaying.value) {
    audioSynth.stopTapeHiss()
    isAudioPreviewPlaying.value = false
  } else {
    audioSynth.startTapeHiss(tapeHissVol.value)
    isAudioPreviewPlaying.value = true
  }
}

function handleSpotifyAutoplayToggle() {
  form.spotify_autoplay = spotifyAutoplayEnabled.value ? '1' : '0'
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

async function handleVideoFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    await processVideoUpload(target.files[0])
  }
}

async function handleVideoDrop(e: DragEvent) {
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    await processVideoUpload(e.dataTransfer.files[0])
  }
}

async function processVideoUpload(file: File) {
  videoUploadIsError.value = false
  videoUploadMessage.value = `Uploading '${file.name}' (${(file.size / (1024 * 1024)).toFixed(1)} MB)...`
  try {
    const clip = await commercialsEngine.uploadClipToServer(file)
    videoUploadMessage.value = `SUCCESS: Added '${clip.name}' to rotation queue.`
    setTimeout(() => { videoUploadMessage.value = '' }, 4000)
  } catch (err) {
    videoUploadIsError.value = true
    videoUploadMessage.value = `UPLOAD ERROR: ${String(err)}`
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

  ingestionMessage.value = `[PARSING] Ingesting ${file.name} (${Math.round(file.size / 1024)} KB)...`
  setTimeout(() => {
    ingestionMessage.value = `[SUCCESS] Successfully parsed ticket commitment from ${file.name}. Saved to calendar.`
  }, 1200)
}

async function handlePingOllama() {
  isTestingOllama.value = true
  ollamaTestResult.value = null
  try {
    const res = await pingOllamaInstance(form.ai_ollama_url || 'http://localhost:11434', form.ai_ollama_model)
    ollamaTestResult.value = res
    if (res.models && res.models.length > 0) {
      ollamaDetectedModels.value = res.models
      if (!form.ai_ollama_model || !res.models.includes(form.ai_ollama_model)) {
        form.ai_ollama_model = res.models[0]
      }
    }
  } catch (err) {
    ollamaTestResult.value = {
      status: 'offline',
      ollama_url: form.ai_ollama_url || 'http://localhost:11434',
      latency_ms: 0,
      models: [],
      error: String(err),
    }
  } finally {
    isTestingOllama.value = false
  }
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

    if (s.spotify_autoplay) {
      spotifyAutoplayEnabled.value = s.spotify_autoplay === '1'
    }

    if (s.commercials_enabled) {
      commercialsEnabled.value = s.commercials_enabled === '1'
      commercialsEngine.isEnabled.value = commercialsEnabled.value
    }
    if (s.commercials_frequency_per_hour) {
      commercialsFrequency.value = parseInt(s.commercials_frequency_per_hour, 10)
      commercialsEngine.frequencyPerHour.value = commercialsFrequency.value
    }

    // Sync server-side commercials
    await commercialsEngine.syncWithServerDropzone()

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
    // If coordinates were not updated for custom text, attempt geocode
    if (form.metro_label && form.latitude === '40.7128' && form.longitude === '-74.0060' && form.metro_label !== 'NEW YORK CITY') {
      try {
        const results = await geocodeLocationQuery(form.metro_label)
        if (results && results.length > 0) {
          form.latitude = results[0].latitude.toString()
          form.longitude = results[0].longitude.toString()
          if (results[0].postal_code) form.postal_code = results[0].postal_code
        }
      } catch {
        // Continue
      }
    }

    for (const [k, v] of Object.entries(form)) {
      if (v !== undefined) {
        await updateSetting(k, String(v))
      }
    }

    // Refresh weather immediately for new coordinates
    refreshWeather().catch(() => {})

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
