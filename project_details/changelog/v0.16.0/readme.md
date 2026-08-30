# Release v0.16.0: 100% Sports League Coverage, Retro Commercials Engine & Auto-Update Hub

## Overview
Release v0.16.0 introduces comprehensive 100% sports franchise coverage across all major leagues (NFL, NBA, MLB, NHL, MLS, EPL), a retro 1990s television commercials and station bumpers engine, an overlayed translucent Spotify divider ticker, and an auto-update notification system with plain English rate limit resilience.

## Visual Showcase (New York City Metro Area)

### 16:9 Landscape Dashboard with Spotify Translucent Ticker
![OpenPrevue 16:9 Landscape Dashboard](./dashboard_landscape.png)

### 9:16 Vertical Portrait Kiosk
![OpenPrevue 9:16 Vertical Portrait Kiosk](./dashboard_portrait.png)

### Small Screen 7" Raspberry Pi Display
![OpenPrevue Small Screen Display](./dashboard_small_pi.png)

### Settings Control Center & Audio Synthesizer
![OpenPrevue Settings Control Center](./settings_control_center.png)

---

## Key Deliverables

### 1. 100% Sports League Franchise Coverage (`sportsAssets.ts`)
* **NFL (All 32 Teams):** Cardinals, Falcons, Ravens, Bills, Panthers, Bears, Bengals, Browns, Cowboys, Broncos, Lions, Packers, Texans, Colts, Jaguars, Chiefs, Raiders, Chargers, Rams, Dolphins, Vikings, Patriots, Saints, Giants, Jets, Eagles, Steelers, 49ers, Seahawks, Buccaneers, Titans, Commanders.
* **NBA (All 30 Teams):** Hawks, Celtics, Nets, Hornets, Bulls, Cavaliers, Mavericks, Nuggets, Pistons, Warriors, Rockets, Pacers, Clippers, Lakers, Grizzlies, Heat, Bucks, Timberwolves, Pelicans, Knicks, Thunder, Magic, 76ers, Suns, Trail Blazers, Kings, Spurs, Raptors, Jazz, Wizards.
* **MLB (All 30 Teams):** Diamondbacks, Braves, Orioles, Red Sox, Cubs, White Sox, Reds, Guardians, Rockies, Tigers, Astros, Royals, Angels, Dodgers, Marlins, Brewers, Twins, Mets, Yankees, Athletics, Phillies, Pirates, Padres, Giants, Mariners, Cardinals, Rays, Rangers, Blue Jays, Nationals.
* **NHL (All 32 Teams):** Ducks, Bruins, Sabres, Flames, Hurricanes, Blackhawks, Avalanche, Blue Jackets, Stars, Red Wings, Oilers, Panthers, Kings, Wild, Canadiens, Predators, Devils, Islanders, Rangers, Senators, Flyers, Penguins, Sharks, Kraken, Blues, Lightning, Maple Leafs, Utah Hockey Club, Canucks, Golden Knights, Capitals, Jets.
* **MLS & Premier League (37 Clubs):** All 29 MLS teams (Inter Miami, Austin FC, Dynamo, LAFC, Sounders, etc.) and Premier League clubs (Arsenal, Chelsea, Liverpool, Man City, Man United, Newcastle, Tottenham, Aston Villa).
* **Vector Matchup Generator:** High-fidelity retro 1990s head-to-head graphics with vector helmets, team shields, primary/secondary franchise colors, and odds.

### 2. Retro Commercials & Station Bumpers Engine (`commercialsEngine.ts`)
* **1990s Video Break Engine:** Periodically interrupts the top preview quadrant with retro station IDs, local commercials, or VHS bumpers.
* **Frequency Slider:** User-controlled slider from 1 to 10 commercials per hour (e.g. 4/hr plays one clip every ~15 minutes).
* **Local Video Dropzone:** Drag and drop `.mp4` and `.webm` clips directly in Settings to queue custom video files.
* **Audio Ducking:** Seamlessly pauses/ducks background Muzak while the video plays and resumes automatically upon conclusion.

### 3. Overlayed Translucent Spotify Divider Ticker (`SpotlightPane.vue`)
* **Translucent Glass Ribbon:** Positioned across the bottom edge of the top preview pane as a divider before the scrolling schedule below.
* **Equalizer & Marquee:** Animated Spotify visualizer bars with live track/audio info ticker.
* **Playlist Launcher:** 1-click launch button linked to the official OpenPrevue Spotify playlist.

### 4. Auto-Update Notification Hub & Privacy OOBE (`updater.py`, `UpdateToast.vue`)
* **Privacy-First OOBE Default:** Out-of-the-box configuration defaults to `disabled` (zero automated external network calls).
* **Configurable Cadence:** Choose from `disabled`, `weekly`, `daily`, or `on_boot`.
* **Plain English Rate Limit Handling:** Friendly, non-technical explanations with exact minute countdowns parsed from GitHub headers.
* **Retro Update Toast:** CRT-styled floating toast notification with dismiss persistence and header bar badge.

### 5. Automated Verification
* 55 passing unit and integration tests in pytest.
* Zero error TypeScript compilation and Vite production build.
