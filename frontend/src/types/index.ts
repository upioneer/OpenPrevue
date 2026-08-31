export interface TicketLink {
  id: number
  source: string
  url: string
  label?: string
  created_at: string
}

export interface EventItem {
  id: string
  venue_id: string
  title: string
  description?: string
  category: string
  start_time: string
  end_time?: string
  price_min?: number
  price_max?: number
  currency: string
  image_url?: string
  ticket_url: string
  source: string
  source_event_id?: string
  is_featured: number
  has_ticket?: number
  status: string
  venue_name?: string
  venue_address?: string
  venue_city?: string
  venue_state?: string
  ticket_links?: TicketLink[]
  last_seen_at?: string
  created_at?: string
}

export interface VenueItem {
  id: string
  name: string
  address?: string
  city?: string
  state?: string
  postal_code?: string
  latitude?: number
  longitude?: number
  timezone: string
  custom_order: number
  is_active: number
  needs_review: number
}

export interface WeatherData {
  temperature: number
  apparent_temperature: number
  weather_code: number
  condition: string
  humidity: number
  wind_speed: number
  temperature_unit: string
  wind_speed_unit: string
  updated_at: string
}

export interface HealthData {
  status: string
  uptime_seconds: number
  database: string
  scheduler: string
  providers: Record<string, {
    status: string
    last_sync?: string
    events_cached: number
    error?: string
  }>
  telegram_bot: string
}

export interface UpdateStatusResponse {
  current_version: string
  latest_version: string
  update_available: boolean
  release_url: string
  release_title: string
  release_notes: string
  last_checked: string | null
  update_check_interval: string
  rate_limit_remaining?: number | null
  rate_limit_reset_minutes?: number | null
  is_rate_limited?: boolean
  user_message?: string | null
  last_error?: string | null
}

export interface OllamaPingResponse {
  status: string
  ollama_url: string
  latency_ms: number
  models: string[]
  version?: string | null
  error?: string | null
}

export interface GeocodeResult {
  name: string
  admin1?: string | null
  country?: string | null
  metro_label: string
  latitude: number
  longitude: number
  postal_code?: string | null
  display_label: string
}

export interface SpotifyMetadataResponse {
  title: string
  author_name?: string | null
  thumbnail_url?: string | null
  embed_url?: string | null
  playlist_url: string
  provider: string
}

export interface SystemSettings {
  postal_code: string
  metro_label: string
  latitude: string
  longitude: string
  radius_miles: string
  autoscroll_speed: string
  grid_density?: 'classic_tv' | 'balanced' | 'dense' | string
  scroll_pause_duration?: string
  scroll_page_interval?: string
  marquee_rotation_seconds: string
  scanline_intensity: string
  phosphor_glow: string
  crt_curvature: string
  vhs_tracking_noise: string
  time_format: string
  sync_interval_hours: string
  update_check_interval?: string
  auto_update_notifs?: string
  ai_ollama_url?: string
  ai_ollama_model?: string
  [key: string]: string | undefined
}
