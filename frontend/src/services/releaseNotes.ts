export interface ReleaseNote {
  version: string
  title: string
  highlights: string[]
}

export const RECENT_RELEASES: ReleaseNote[] = [
  {
    version: '0.25.0',
    title: 'First-Launch Onboarding Guide, Post-Update Changelog & Multi-Tier Settings Persistence',
    highlights: [
      'First-Launch Operator Onboarding Modal guiding new users to Settings, Curated 90s Spotify Radio, Ticket Entry, Ollama AI, and Operator Docs.',
      'Post-Update Changelog Modal automatically presenting release highlights on upgrades with suppression preference.',
      'Settings Tab 11 Modal Preference Cards with [ PREVIEW ] and [ RE-ENABLE ] controls.',
      'Automated Multi-Tier Settings Persistence saving openprevue_settings_backup.json on disk upon every change.',
      'Automated Boot Configuration Restore recovering AI endpoints and preferences on fresh container launches before seeding.',
      'Settings Tab 10 Configuration Backup & Recovery Center with JSON export, JSON import, and server disk restore.',
      'Browser Local Cache Mirror with auto-detection banner offering 1-click restoration if volumes were unmounted.',
      'Fortified Docker volume persistence with VOLUME ["/app/data"] and in-place upgrade mount preservation.'
    ]
  },
  {
    version: '0.24.0',
    title: 'System Health Ledger, CRT Event Viewer & Travel Wishlist Sync',
    highlights: [
      'Real-Time System Health & Connectivity Ledger in Settings Tab 10 monitoring SQLite WAL, scheduler, speech, and circuit breakers.',
      'Live retro CRT Activity & Audit Event Viewer terminal tracking operational journal logs in real time.',
      'User Onboarding & Bells-and-Whistles Tour in Settings Tab 11.',
      'TripAdvisor & Viator Wishlist Ingestion with dedicated sync triggers and multi-event scraping.',
      'Zero-click real-time phosphor auto-save persistence across all settings.',
      'Listing Window & Empty Venue suppression filter (?filter=active) for kiosk screens.',
      'Prominently discoverable [+TKT] ticket stub button and genre badging.'
    ]
  },
  {
    version: '0.23.0',
    title: 'Direct Media Volume Routing & Multi-Display Kiosk Architecture',
    highlights: [
      'Direct master volume routing regulating YouTube video loudness and Spotify playback.',
      'Decoupled ambient analog tape hiss into independent preference (0% default).',
      'Multi-screen URL overrides (?density=, ?kiosk=1, ?filter=active) for running unlimited displays from one headend.',
      'Deployment & Kiosk Guide in Settings Tab 11 with copyable bookmark profiles and Raspberry Pi recipes.'
    ]
  }
]

export function getReleaseNotes(version?: string): ReleaseNote {
  if (version) {
    const cleanVer = version.replace(/^v/, '')
    const match = RECENT_RELEASES.find((r) => r.version === cleanVer)
    if (match) return match
  }
  return RECENT_RELEASES[0]
}
