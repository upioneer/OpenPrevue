<template>
  <div class="w-full h-full bg-[#000044] border-b-2 border-[#FFFF00] flex flex-col justify-between overflow-hidden select-none font-mono relative">
    <!-- TOP 2-COLUMN SPLIT PREVIEW BODY (CLASSIC 1990S PREVUE CABLE LAYOUT) -->
    <div class="flex-1 w-full flex flex-row items-stretch min-h-0 overflow-hidden px-2 pt-1.5 gap-3">
      <!-- LEFT COLUMN (48% on desktop / 45% mobile): FEATURED EVENT ARTWORK / CRT GRAPHICS / SPORTS MATCHUP VS CARD -->
      <div class="w-[48%] h-full flex flex-col justify-between border-2 border-[#00FFFF] bg-[#000022] overflow-hidden relative shadow-inner">
        <!-- 1. Live Sports Matchup Graphic Card (When Category is Sports and teams are parsed) -->
        <div
          v-if="isSportsCategory && matchupTeams"
          class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000044] via-[#000022] to-[#000011] overflow-hidden"
        >
          <!-- Matchup Header with Official League Emblem -->
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <img
                v-if="leagueBranding?.logoUrl"
                :src="leagueBranding.logoUrl"
                :alt="leagueBranding.shortName"
                class="h-5 w-auto object-contain bg-white/10 px-1 py-0.5 rounded-xs shrink-0 drop-shadow"
              />
              <span class="text-[#FFFF00] font-black uppercase tracking-wider truncate">
                [ {{ leagueBranding?.shortName ? leagueBranding.shortName + ' LIVE MATCHUP' : 'LIVE MATCHUP' }} ]
              </span>
            </div>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'MAIN ARENA' }}
            </span>
          </div>

          <!-- Extra Large Team VS Badges & Official Franchise Colors -->
          <div class="flex items-center justify-around py-1 text-center my-auto w-full px-1">
            <!-- Home Team Card -->
            <div class="flex flex-col items-center space-y-1.5 sm:space-y-2 w-[44%]">
              <div
                class="w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 lg:w-36 lg:h-36 xl:w-40 xl:h-40 rounded-full border-3 sm:border-4 p-2 sm:p-3 flex items-center justify-center font-black relative overflow-hidden shadow-2xl transition-transform hover:scale-105"
                :style="{
                  borderColor: teamABranding?.secondaryColor || '#FFFF00',
                  backgroundColor: teamABranding?.primaryColor || '#000044',
                  boxShadow: `0 0 20px ${teamABranding?.secondaryColor || 'rgba(255,255,0,0.6)'}`
                }"
              >
                <!-- Large Logo Image with High-Res Acronym Fallback -->
                <img
                  v-if="teamABranding?.logoUrl && !teamALogoError"
                  :src="teamABranding.logoUrl"
                  :alt="teamABranding.name"
                  class="w-full h-full object-contain drop-shadow-lg"
                  @error="teamALogoError = true"
                />
                <span
                  v-else
                  class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl tracking-wider"
                  :style="{ color: teamABranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamABranding?.shortName || matchupTeams.teamA.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm md:text-base lg:text-lg font-black text-[#FFFFFF] truncate w-full leading-tight uppercase drop-shadow">
                {{ teamABranding?.name || matchupTeams.teamA }}
              </span>
            </div>

            <!-- Prominent Broadcast VS Lightning Graphic -->
            <div class="flex flex-col items-center shrink-0 px-2 sm:px-3">
              <span class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl text-[#FF4444] animate-pulse drop-shadow-[0_0_14px_rgba(255,68,68,0.95)]">
                VS
              </span>
              <span class="text-[10px] sm:text-xs text-[#00FFFF] font-black tracking-widest uppercase mt-0.5">MATCHUP</span>
            </div>

            <!-- Away Team Card -->
            <div class="flex flex-col items-center space-y-1.5 sm:space-y-2 w-[44%]">
              <div
                class="w-20 h-20 sm:w-24 sm:h-24 md:w-32 md:h-32 lg:w-36 lg:h-36 xl:w-40 xl:h-40 rounded-full border-3 sm:border-4 p-2 sm:p-3 flex items-center justify-center font-black relative overflow-hidden shadow-2xl transition-transform hover:scale-105"
                :style="{
                  borderColor: teamBBranding?.secondaryColor || '#00FFFF',
                  backgroundColor: teamBBranding?.primaryColor || '#000044',
                  boxShadow: `0 0 20px ${teamBBranding?.secondaryColor || 'rgba(0,255,255,0.6)'}`
                }"
              >
                <!-- Large Logo Image with High-Res Acronym Fallback -->
                <img
                  v-if="teamBBranding?.logoUrl && !teamBLogoError"
                  :src="teamBBranding.logoUrl"
                  :alt="teamBBranding.name"
                  class="w-full h-full object-contain drop-shadow-lg"
                  @error="teamBLogoError = true"
                />
                <span
                  v-else
                  class="font-black text-xl sm:text-2xl md:text-3xl lg:text-4xl tracking-wider"
                  :style="{ color: teamBBranding?.textColor || '#FFFFFF' }"
                >
                  {{ teamBBranding?.shortName || matchupTeams.teamB.slice(0, 3).toUpperCase() }}
                </span>
              </div>
              <span class="text-xs sm:text-sm md:text-base lg:text-lg font-black text-[#FFFFFF] truncate w-full leading-tight uppercase drop-shadow">
                {{ teamBBranding?.name || matchupTeams.teamB }}
              </span>
            </div>
          </div>

          <!-- Matchup Footer Ribbon with Provider Tag -->
          <div class="bg-[#000066] border border-[#00FFFF] px-2 py-0.5 sm:py-1 flex items-center justify-between text-xs sm:text-sm text-[#00FFFF] font-black uppercase truncate shrink-0">
            <span>HEAD TO HEAD BROADCAST</span>
            <span class="text-[#FFFF00] text-[11px]">[ {{ providerBranding.badgeText }} ]</span>
          </div>
        </div>

        <!-- 2. Live Concert & Music Headliner Card -->
        <div
          v-else-if="isMusicCategory && (!currentEvent?.image_url || imageErrorMap[currentEvent?.id])"
          class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000055] via-[#000033] to-[#000022] overflow-hidden"
        >
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="w-2.5 h-2.5 bg-[#00FFFF] inline-block animate-ping rounded-full"></span>
              <span class="text-[#FFFF00] font-black uppercase tracking-wider truncate">
                [ LIVE CONCERT HEADLINER ]
              </span>
            </div>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'LIVE STAGE' }}
            </span>
          </div>

          <!-- Center Animated Vinyl & Spectrum Visualizer -->
          <div class="flex flex-col items-center justify-center my-auto space-y-2 py-1">
            <div class="w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-full border-3 border-[#00FFFF] bg-[#000044] flex items-center justify-center shadow-[0_0_20px_rgba(0,255,255,0.4)] relative">
              <div class="w-16 h-16 sm:w-20 sm:h-20 md:w-22 md:h-22 rounded-full border-2 border-dashed border-[#FFFF00]/60 flex items-center justify-center animate-spin-slow">
                <div class="w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 rounded-full bg-[#FFFF00] text-[#000033] font-black flex items-center justify-center text-[10px] sm:text-xs border-2 border-white shadow-inner">
                  LIVE
                </div>
              </div>
            </div>

            <div class="text-center px-2">
              <span class="text-sm sm:text-base md:text-lg lg:text-xl font-black text-[#FFFF00] uppercase tracking-wide line-clamp-1 drop-shadow-[0_0_8px_rgba(255,255,0,0.6)]">
                {{ currentEvent?.title }}
              </span>
            </div>

            <!-- 18-Band Vintage Phosphor Green / Yellow Equalizer Spectrum -->
            <div class="flex items-end justify-center space-x-1 h-7 sm:h-8 w-full max-w-[260px] px-2 bg-[#000022] border border-[#333366] py-1 rounded-xs">
              <span
                v-for="n in 18"
                :key="n"
                class="w-1 bg-gradient-to-t from-[#00FF00] via-[#00FFFF] to-[#FFFF00] rounded-xs transition-all duration-300 animate-pulse"
                :style="{
                  height: `${Math.max(20, (Math.sin(n * 1.4) * 38 + 58))}%`,
                  animationDelay: `${(n * 80) % 800}ms`
                }"
              ></span>
            </div>
          </div>

          <div class="bg-[#000066] border border-[#00FFFF] px-2 py-0.5 sm:py-1 flex items-center justify-between text-xs sm:text-sm text-[#00FFFF] font-black uppercase truncate shrink-0">
            <span>HI-FI STEREO BROADCAST</span>
            <span class="text-[#FFFF00] text-[11px]">[ {{ providerBranding.badgeText }} ]</span>
          </div>
        </div>

        <!-- 3. Broadway & Performing Arts Showcase Card -->
        <div
          v-else-if="isTheaterCategory && (!currentEvent?.image_url || imageErrorMap[currentEvent?.id])"
          class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000055] via-[#000033] to-[#000022] overflow-hidden"
        >
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="w-2.5 h-2.5 bg-[#FFFF00] inline-block animate-ping rounded-full"></span>
              <span class="text-[#FFFF00] font-black uppercase tracking-wider truncate">
                [ BROADWAY & THEATER SPOTLIGHT ]
              </span>
            </div>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'THEATER STAGE' }}
            </span>
          </div>

          <!-- Center Stage Graphic with Gold Vector Masks -->
          <div class="flex flex-col items-center justify-center my-auto space-y-2 py-1">
            <div class="w-18 h-18 sm:w-22 sm:h-22 md:w-24 md:h-24 rounded-full border-3 border-[#FFFF00] bg-[#000044] flex items-center justify-center shadow-[0_0_20px_rgba(255,255,0,0.4)] p-3">
              <!-- Vector Drama Masks Icon -->
              <svg viewBox="0 0 24 24" class="w-full h-full fill-[#FFFF00] drop-shadow" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm7-6c-.83 0-1.5-.67-1.5-1.5S16.17 8 17 8s1.5.67 1.5 1.5S17.83 11 17 11zm-10 0c-.83 0-1.5-.67-1.5-1.5S6.17 8 7 8s1.5.67 1.5 1.5S7.83 11 7 11z"/>
              </svg>
            </div>

            <div class="text-center px-2">
              <span class="text-sm sm:text-base md:text-lg lg:text-xl font-black text-[#FFFF00] uppercase tracking-wide line-clamp-2 drop-shadow-[0_0_8px_rgba(255,255,0,0.6)]">
                {{ currentEvent?.title }}
              </span>
            </div>

            <div class="bg-[#000033] border border-[#FFFF00] px-3 py-1 text-center text-xs text-[#00FFFF] font-black uppercase tracking-widest">
              STAGE PRODUCTION // CRITIC ACCLAIMED
            </div>
          </div>

          <div class="bg-[#000066] border border-[#00FFFF] px-2 py-0.5 sm:py-1 flex items-center justify-between text-xs sm:text-sm text-[#00FFFF] font-black uppercase truncate shrink-0">
            <span>LIVE STAGE PERFORMANCE</span>
            <span class="text-[#FFFF00] text-[11px]">[ {{ providerBranding.badgeText }} ]</span>
          </div>
        </div>

        <!-- 4. Stand-Up Comedy Showcase Card -->
        <div
          v-else-if="isComedyCategory && (!currentEvent?.image_url || imageErrorMap[currentEvent?.id])"
          class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000055] via-[#000033] to-[#000022] overflow-hidden"
        >
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="w-2.5 h-2.5 bg-[#FFFF00] inline-block animate-ping rounded-full"></span>
              <span class="text-[#FFFF00] font-black uppercase tracking-wider truncate">
                [ STAND-UP COMEDY NIGHT ]
              </span>
            </div>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'COMEDY CLUB' }}
            </span>
          </div>

          <!-- Center Studio Mic Graphic -->
          <div class="flex flex-col items-center justify-center my-auto space-y-2 py-1">
            <div class="w-18 h-18 sm:w-22 sm:h-22 md:w-24 md:h-24 rounded-full border-3 border-[#00FFFF] bg-[#000044] flex items-center justify-center shadow-[0_0_20px_rgba(0,255,255,0.4)] p-3">
              <!-- Vector Studio Microphone Icon -->
              <svg viewBox="0 0 24 24" class="w-full h-full fill-[#FFFF00] drop-shadow" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.49 6-3.31 6-6.72h-1.7z"/>
              </svg>
            </div>

            <div class="text-center px-2">
              <span class="text-sm sm:text-base md:text-lg lg:text-xl font-black text-[#FFFF00] uppercase tracking-wide line-clamp-2 drop-shadow-[0_0_8px_rgba(255,255,0,0.6)]">
                {{ currentEvent?.title }}
              </span>
            </div>

            <div class="bg-[#000033] border border-[#00FFFF] px-3 py-1 text-center text-xs text-[#00FFFF] font-black uppercase tracking-widest">
              LIVE HEADLINER SET // ADULTS 18+
            </div>
          </div>

          <div class="bg-[#000066] border border-[#00FFFF] px-2 py-0.5 sm:py-1 flex items-center justify-between text-xs sm:text-sm text-[#00FFFF] font-black uppercase truncate shrink-0">
            <span>LIVE CLUB RECORDING</span>
            <span class="text-[#FFFF00] text-[11px]">[ {{ providerBranding.badgeText }} ]</span>
          </div>
        </div>

        <!-- 5. Featured Event Artwork Image with CRT Gradient Overlay -->
        <div v-else-if="currentEvent?.image_url && !imageErrorMap[currentEvent?.id]" class="w-full h-full relative overflow-hidden flex items-center justify-center bg-black">
          <img
            :src="currentEvent.image_url"
            :alt="currentEvent.title"
            class="w-full h-full object-cover opacity-90 transition-transform duration-700 hover:scale-105"
            @error="handleImageError"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-[#000044] via-transparent to-black/40 pointer-events-none"></div>
          <div class="absolute top-2 left-2 bg-[#0000AA]/90 border border-[#FFFF00] px-2.5 py-0.5 text-xs sm:text-sm font-black text-[#FFFF00] uppercase tracking-wider shadow">
            HEADLINE PREVIEW
          </div>
          <div class="absolute top-2 right-2 bg-[#000022]/90 border border-[#00FFFF] px-2 py-0.5 text-[11px] font-black text-[#00FFFF] uppercase tracking-wider shadow">
            {{ providerBranding.badgeText }}
          </div>
        </div>

        <!-- 6. Fallback Community / Travel Showcase Card -->
        <div v-else class="w-full h-full flex flex-col justify-between p-2 sm:p-3 bg-gradient-to-b from-[#000055] via-[#000033] to-[#000022] overflow-hidden">
          <div class="flex items-center justify-between border-b border-[#00FFFF]/50 pb-1 text-xs sm:text-sm shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="w-2.5 h-2.5 bg-[#00FF00] inline-block animate-ping rounded-full"></span>
              <span class="text-[#00FF00] font-black uppercase tracking-wider truncate">
                [ {{ currentEvent?.category ? currentEvent.category.toUpperCase() + ' SPOTLIGHT' : 'COMMUNITY SPOTLIGHT' }} ]
              </span>
            </div>
            <span class="text-[#00FFFF] font-black truncate max-w-[180px] text-xs sm:text-sm uppercase">
              {{ currentEvent?.venue_name || 'LOCAL AREA' }}
            </span>
          </div>

          <!-- Center Experience Compass Vector -->
          <div class="flex flex-col items-center justify-center my-auto space-y-2 py-1">
            <div class="w-18 h-18 sm:w-22 sm:h-22 md:w-24 md:h-24 rounded-full border-3 border-[#00FF00] bg-[#000044] flex items-center justify-center shadow-[0_0_20px_rgba(0,255,0,0.4)] p-3">
              <svg viewBox="0 0 24 24" class="w-full h-full fill-[#00FF00] drop-shadow" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-2.5l7.51-3.49L17.5 6.5 9.99 9.99 6.5 17.5zm5.5-6.6c.61 0 1.1.49 1.1 1.1s-.49 1.1-1.1 1.1-1.1-.49-1.1-1.1.49-1.1 1.1-1.1z"/>
              </svg>
            </div>

            <div class="text-center px-2">
              <span class="text-sm sm:text-base md:text-lg lg:text-xl font-black text-[#FFFF00] uppercase tracking-wide line-clamp-2 drop-shadow-[0_0_8px_rgba(255,255,0,0.6)]">
                {{ currentEvent?.title }}
              </span>
            </div>

            <div class="bg-[#000033] border border-[#00FF00] px-3 py-1 text-center text-xs text-[#00FFFF] font-black uppercase tracking-widest">
              FEATURED METRO EXPERIENCE
            </div>
          </div>

          <div class="bg-[#000066] border border-[#00FF00] px-2 py-0.5 sm:py-1 flex items-center justify-between text-xs sm:text-sm text-[#00FF00] font-black uppercase truncate shrink-0">
            <span>LOCAL ADMISSION</span>
            <span class="text-[#FFFF00] text-[11px]">[ {{ providerBranding.badgeText }} ]</span>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN (52%): RETRO CABLE BULLETIN TEXT, DETAILS & TICKET PASS -->
      <div class="w-[52%] h-full flex flex-col justify-between py-1 pr-1 font-mono min-h-0 overflow-hidden">
        <div class="space-y-1.5 overflow-hidden">
          <!-- Top Meta Tag with League and Provider Badges -->
          <div class="flex items-center justify-between text-xs sm:text-sm border-b border-[#333366] pb-1 shrink-0">
            <div class="flex items-center space-x-1.5 truncate">
              <span class="text-[#00FFFF] font-black tracking-wider uppercase truncate text-xs sm:text-sm">
                [ {{ currentEvent?.category || 'FEATURED' }} ]
              </span>

              <!-- League Logo Badge if Applicable -->
              <span
                v-if="leagueBranding"
                class="px-1.5 py-0.5 rounded-xs font-black text-[10px] sm:text-[11px] flex items-center space-x-1 border shrink-0 shadow-sm"
                :style="{
                  backgroundColor: leagueBranding.primaryColor,
                  borderColor: '#FFFF00',
                  color: leagueBranding.textColor
                }"
                :title="leagueBranding.name"
              >
                <img v-if="leagueBranding.logoUrl" :src="leagueBranding.logoUrl" :alt="leagueBranding.shortName" class="h-3.5 w-auto object-contain" />
                <span>{{ leagueBranding.shortName }}</span>
              </span>

              <!-- Provider Badge with Official Colors -->
              <span
                class="px-1.5 py-0.5 rounded-xs font-black text-[10px] sm:text-xs border shrink-0"
                :style="{
                  borderColor: providerBranding.brandColor,
                  backgroundColor: '#000022',
                  color: providerBranding.textColor
                }"
                :title="providerBranding.name"
              >
                [ {{ providerBranding.badgeText }} ]
              </span>

              <span
                v-if="currentEvent?.has_ticket === 1"
                class="bg-[#00FF00] text-[#000033] text-xs px-2 py-0.5 font-black rounded-xs shadow-[0_0_6px_rgba(0,255,0,0.8)] shrink-0"
              >
                [TICKET OWNED]
              </span>
            </div>
            <span class="text-[#8888AA] text-xs sm:text-sm shrink-0 font-black">
              SPOTLIGHT {{ currentIndex + 1 }} OF {{ featuredEvents.length }}
            </span>
          </div>

          <!-- Venue Name -->
          <div class="text-xs sm:text-sm md:text-base text-[#E0E0E0] uppercase tracking-wide truncate shrink-0 font-bold">
            VENUE: <span class="text-[#FFFFFF] font-black">{{ currentEvent?.venue_name || 'MAIN STAGE' }}</span>
          </div>

          <!-- Event Title (Large Chunky 1990s TV Typography) -->
          <div class="text-base sm:text-lg md:text-xl lg:text-2xl font-black text-[#FFFF00] leading-tight line-clamp-2 tracking-wide drop-shadow-md uppercase shrink-0">
            {{ currentEvent?.title || 'NO FEATURED EVENTS SCHEDULED' }}
          </div>

          <!-- Date & Time -->
          <div class="text-xs sm:text-sm md:text-base text-[#00FFFF] font-bold truncate shrink-0">
            DATE: <span class="text-[#00FF00] font-black">{{ formattedDate }}</span>
          </div>

          <!-- Price Range & Ticket Provider -->
          <div class="text-xs sm:text-sm md:text-base text-[#00FF00] font-bold truncate shrink-0 flex items-center space-x-2">
            <span>TICKETS: <span class="text-[#FFFF00] font-black">{{ formattedPrice }}</span></span>
            <span class="text-[#8888AA] text-xs">VIA {{ providerBranding.name.toUpperCase() }}</span>
          </div>

          <!-- Description Snippet -->
          <p v-if="currentEvent?.description" class="text-xs sm:text-sm text-[#A0A0C0] line-clamp-2 leading-relaxed pt-0.5 hidden sm:block overflow-hidden font-medium">
            {{ currentEvent.description }}
          </p>
        </div>

        <!-- Bottom: High-Contrast Scannable Box Office Mobile QR Pass & Rotation Dots -->
        <div class="flex items-center justify-between pt-1.5 border-t border-[#333366] shrink-0">
          <div class="flex items-center space-x-2 sm:space-x-3">
            <!-- Large High-Contrast Scannable QR Code Pass (Engineered for Scanline Resistance) -->
            <div
              v-if="qrCodeDataUrl"
              class="bg-white p-1 rounded-xs border-2 border-[#FFFF00] shadow-[0_0_10px_rgba(255,255,0,0.7)] shrink-0 cursor-pointer transition-transform hover:scale-110"
              @click="isQrModalOpen = true"
              title="Click to expand high-resolution ticket QR pass"
            >
              <img
                :src="qrCodeDataUrl"
                alt="Ticket QR Pass"
                class="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 object-contain"
              />
            </div>
            <div class="text-xs text-[#8888AA] leading-tight hidden sm:block">
              <span class="text-[#FFFF00] font-black block tracking-wider text-xs">{{ providerBranding.badgeText }}</span>
              <span class="text-[#00FF00] font-black text-xs">BOX OFFICE QR PASS</span>
            </div>
          </div>

          <!-- Rotation Indicator Dots -->
          <div class="flex space-x-1.5 sm:space-x-2">
            <button
              v-for="(_, idx) in featuredEvents.slice(0, 8)"
              :key="idx"
              type="button"
              class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full transition-all cursor-pointer"
              :class="idx === currentIndex ? 'bg-[#FFFF00] scale-125 shadow-[0_0_6px_rgba(255,255,0,0.8)]' : 'bg-[#333366] hover:bg-[#8888AA]'"
              @click="setIndex(idx)"
            ></button>
          </div>
        </div>
      </div>
    </div>

    <!-- OVERLAYED TRANSLUCENT SPOTIFY MARQUEE TICKER (IN-FLOW BOTTOM EDGE) -->
    <div class="h-7 sm:h-8 w-full bg-[#000022]/90 backdrop-blur-xs border-t border-[#1DB954]/50 flex items-center justify-between px-3 text-xs sm:text-sm font-mono text-[#E0E0E0] shrink-0 select-none shadow-md z-10">
      <!-- Left: Equalizer Graphic & Spotify Branding -->
      <div class="flex items-center space-x-2 shrink-0">
        <button
          type="button"
          class="flex items-center space-x-1.5 cursor-pointer hover:opacity-80 transition-opacity"
          @click="openSpotifyModal"
          title="Open Spotify Audio Player"
        >
          <div class="flex items-end space-x-0.5 h-3.5 text-[#1DB954]">
            <span class="w-0.5 bg-current animate-pulse h-2"></span>
            <span class="w-0.5 bg-current animate-pulse h-3.5"></span>
            <span class="w-0.5 bg-current animate-pulse h-2"></span>
          </div>
          <span class="font-black text-xs sm:text-sm tracking-wider text-[#1DB954]">
            SPOTIFY
          </span>
        </button>
      </div>

      <!-- Center: Marquee Stream Telemetry -->
      <div class="flex-1 overflow-hidden ml-4 mr-2 text-center">
        <div class="inline-block whitespace-nowrap text-xs text-[#FFFF00] font-bold tracking-widest animate-marquee uppercase">
          NOW STREAMING // OFFICIAL BROADCAST SOUNDTRACK // PLAYLIST: "{{ dynamicSpotifyTitle }}" // CURATED BY {{ dynamicSpotifyAuthor }}
        </div>
      </div>
    </div>

    <!-- Enlarged QR Code Pass Modal -->
    <div
      v-if="isQrModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4"
      @click.self="isQrModalOpen = false"
    >
      <div class="bg-[#000044] border-2 border-[#FFFF00] p-5 max-w-sm w-full text-center space-y-4 shadow-[0_0_24px_rgba(255,255,0,0.6)] font-mono">
        <div class="flex items-center justify-between border-b border-[#333366] pb-2">
          <span class="text-xs font-black text-[#FFFF00] uppercase tracking-wider">[ {{ providerBranding.badgeText }} PASS ]</span>
          <button
            class="text-xs text-[#00FFFF] hover:text-white border border-[#00FFFF] px-2 py-0.5 font-bold cursor-pointer"
            @click="isQrModalOpen = false"
          >
            [ X ]
          </button>
        </div>

        <div class="bg-white p-3 rounded-xs border-4 border-[#00FFFF] inline-block shadow-2xl">
          <img :src="qrCodeDataUrl || ''" alt="Enlarged QR Code" class="w-52 h-52 sm:w-60 sm:h-60 object-contain" />
        </div>

        <div class="space-y-1">
          <div class="text-sm font-black text-[#FFFF00] uppercase">{{ currentEvent?.title }}</div>
          <div class="text-xs text-[#00FF00] font-bold">{{ currentEvent?.venue_name }}</div>
          <div class="text-xs text-[#8888AA]">Scan directly with your phone camera to open tickets.</div>
        </div>

        <div class="pt-2 border-t border-[#333366]">
          <a
            :href="currentEvent?.ticket_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block bg-[#FFFF00] text-[#000033] hover:bg-white px-4 py-2 text-xs sm:text-sm font-black tracking-wider transition-all"
          >
            [ OPEN TICKET LINK DIRECTLY ]
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { fetchSpotifyMetadata } from '../api/client'
import {
  parseMatchup,
  resolveLeagueBranding,
  resolveProviderBranding,
  resolveTeamBranding
} from '../services/sportsTheme'
import { openSpotifyModal } from '../services/spotifyModalState'
import type { EventItem } from '../types'

const props = withDefaults(
  defineProps<{
    events: EventItem[]
    rotationSeconds?: number
  }>(),
  {
    events: () => [],
    rotationSeconds: 20,
  }
)

const currentIndex = ref(0)
const qrCodeDataUrl = ref<string | null>(null)
const isQrModalOpen = ref(false)
const teamALogoError = ref(false)
const teamBLogoError = ref(false)
let rotationTimer: ReturnType<typeof setInterval> | null = null

// Dynamically resolved Spotify playlist details from oEmbed API
const dynamicSpotifyTitle = ref('OPENPREVUE')
const dynamicSpotifyAuthor = ref('UPIONEER')

async function loadSpotifyMeta() {
  try {
    const meta = await fetchSpotifyMetadata()
    if (meta.title) {
      dynamicSpotifyTitle.value = meta.title.toUpperCase()
    }
    if (meta.author_name) {
      dynamicSpotifyAuthor.value = meta.author_name.toUpperCase()
    }
  } catch {
    // Keep defaults
  }
}

// Fallback image error flag per event
const imageErrorMap = ref<Record<string, boolean>>({})

function handleImageError(e: Event) {
  const target = e.target as HTMLImageElement
  if (currentEvent.value) {
    imageErrorMap.value[currentEvent.value.id] = true
  }
  target.style.display = 'none'
}

// Filter featured events, or fallback to all events if none flagged featured
const featuredEvents = computed(() => {
  if (!props.events || props.events.length === 0) return []
  const explicitFeatured = props.events.filter(e => e.is_featured === 1)
  return explicitFeatured.length > 0 ? explicitFeatured : props.events.slice(0, 10)
})

const currentEvent = computed<EventItem | null>(() => {
  if (featuredEvents.value.length === 0) return null
  return featuredEvents.value[currentIndex.value % featuredEvents.value.length]
})

const eventCategory = computed(() => {
  return (currentEvent.value?.category || 'other').toLowerCase()
})

const isSportsCategory = computed(() => {
  return eventCategory.value === 'sports'
})

const isMusicCategory = computed(() => {
  return ['music', 'concert', 'festival'].includes(eventCategory.value)
})

const isTheaterCategory = computed(() => {
  return ['theater', 'theatre', 'broadway', 'performing_arts', 'arts'].includes(eventCategory.value)
})

const isComedyCategory = computed(() => {
  return ['comedy', 'standup'].includes(eventCategory.value)
})

// Parse Sports matchup teams using robust case-insensitive parser
const matchupTeams = computed(() => {
  if (!currentEvent.value || !isSportsCategory.value) return null
  return parseMatchup(currentEvent.value.title)
})

const teamABranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamA)
})

const teamBBranding = computed(() => {
  if (!matchupTeams.value) return null
  return resolveTeamBranding(matchupTeams.value.teamB)
})

const leagueBranding = computed(() => {
  if (matchupTeams.value?.league) {
    return resolveLeagueBranding(matchupTeams.value.league)
  }
  const title = currentEvent.value?.title || ''
  const m = title.match(/\b(NBA|NFL|MLB|NHL|MLS|EPL|PREMIER LEAGUE|F1|NASCAR|UFC)\b/i)
  if (m) {
    return resolveLeagueBranding(m[1])
  }
  return null
})

const providerBranding = computed(() => {
  return resolveProviderBranding(currentEvent.value?.source || currentEvent.value?.ticket_links?.[0]?.source)
})

const formattedDate = computed(() => {
  if (!currentEvent.value?.start_time) return 'TBA'
  try {
    const d = new Date(currentEvent.value.start_time)
    return d.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    }).toUpperCase()
  } catch {
    return currentEvent.value.start_time
  }
})

const formattedPrice = computed(() => {
  if (!currentEvent.value) return 'CHECK BOX OFFICE'
  if (currentEvent.value.price_min && currentEvent.value.price_max) {
    if (currentEvent.value.price_min === currentEvent.value.price_max) {
      return `$${Math.round(currentEvent.value.price_min)}`
    }
    return `$${Math.round(currentEvent.value.price_min)} - $${Math.round(currentEvent.value.price_max)}`
  }
  if (currentEvent.value.price_min) {
    return `FROM $${Math.round(currentEvent.value.price_min)}`
  }
  return 'FREE / ADMISSION AT DOOR'
})

async function generateQrCode() {
  if (!currentEvent.value?.ticket_url) {
    qrCodeDataUrl.value = null
    return
  }
  try {
    // Generate high-resolution, scanline-resistant Level H QR code
    qrCodeDataUrl.value = await QRCode.toDataURL(currentEvent.value.ticket_url, {
      errorCorrectionLevel: 'H',
      margin: 1,
      width: 256,
      color: {
        dark: '#000000',
        light: '#FFFFFF',
      },
    })
  } catch {
    qrCodeDataUrl.value = null
  }
}

function setIndex(idx: number) {
  currentIndex.value = idx
}

function nextSlide() {
  if (featuredEvents.value.length <= 1) return
  currentIndex.value = (currentIndex.value + 1) % featuredEvents.value.length
}

function startTimer() {
  stopTimer()
  const intervalMs = Math.max(5, props.rotationSeconds) * 1000
  rotationTimer = setInterval(nextSlide, intervalMs)
}

function stopTimer() {
  if (rotationTimer) {
    clearInterval(rotationTimer)
    rotationTimer = null
  }
}

watch(currentEvent, () => {
  teamALogoError.value = false
  teamBLogoError.value = false
  generateQrCode()
})

watch(() => props.rotationSeconds, () => {
  startTimer()
})

onMounted(() => {
  generateQrCode()
  startTimer()
  loadSpotifyMeta()
})

onUnmounted(() => {
  stopTimer()
})
</script>
