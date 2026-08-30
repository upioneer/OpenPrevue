import type { EventItem, HealthData, SystemSettings, VenueItem, WeatherData } from '../types'

const API_BASE = '/api/v1'

export async function fetchEvents(params: Record<string, string | number> = {}): Promise<EventItem[]> {
  const query = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      query.append(k, String(v))
    }
  }
  const url = `${API_BASE}/events${query.toString() ? '?' + query.toString() : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Failed to fetch events: ${res.statusText}`)
  return res.json()
}

export async function updateEvent(eventId: string, data: Partial<EventItem>): Promise<EventItem> {
  const res = await fetch(`${API_BASE}/events/${encodeURIComponent(eventId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(`Failed to update event: ${res.statusText}`)
  return res.json()
}

export async function fetchVenues(): Promise<VenueItem[]> {
  const res = await fetch(`${API_BASE}/venues`)
  if (!res.ok) throw new Error(`Failed to fetch venues: ${res.statusText}`)
  return res.json()
}

export async function fetchSettings(): Promise<SystemSettings> {
  const res = await fetch(`${API_BASE}/settings`)
  if (!res.ok) throw new Error(`Failed to fetch settings: ${res.statusText}`)
  return res.json()
}

export async function updateSetting(key: string, value: string): Promise<{ key: string; value: string }> {
  const res = await fetch(`${API_BASE}/settings/${encodeURIComponent(key)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value }),
  })
  if (!res.ok) throw new Error(`Failed to update setting ${key}: ${res.statusText}`)
  return res.json()
}

export async function fetchHealth(): Promise<HealthData> {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error(`Failed to fetch health: ${res.statusText}`)
  return res.json()
}

export async function fetchWeather(): Promise<WeatherData> {
  const res = await fetch(`${API_BASE}/weather`)
  if (!res.ok) throw new Error(`Failed to fetch weather: ${res.statusText}`)
  return res.json()
}

export async function refreshWeather(): Promise<WeatherData> {
  const res = await fetch(`${API_BASE}/weather/refresh`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to refresh weather: ${res.statusText}`)
  return res.json()
}

export async function triggerSync(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/sync`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to trigger sync: ${res.statusText}`)
  return res.json()
}

export async function fetchTelegramStatus(): Promise<{ is_configured: boolean; is_running: boolean; paired_users_count: number }> {
  const res = await fetch(`${API_BASE}/telegram/status`)
  if (!res.ok) throw new Error(`Failed to fetch Telegram status: ${res.statusText}`)
  return res.json()
}

export async function generateTelegramPairCode(): Promise<{ pair_code: string; expires_in_seconds: number }> {
  const res = await fetch(`${API_BASE}/telegram/pair-code`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to generate pairing code: ${res.statusText}`)
  return res.json()
}

export async function fetchTelegramUsers(): Promise<Array<{ chat_id: number; username: string; pair_code: string; paired_at: string; is_active: number }>> {
  const res = await fetch(`${API_BASE}/telegram/users`)
  if (!res.ok) throw new Error(`Failed to fetch Telegram users: ${res.statusText}`)
  return res.json()
}

export async function unpairTelegramUser(chatId: number): Promise<{ status: string; chat_id: number }> {
  const res = await fetch(`${API_BASE}/telegram/users/${chatId}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Failed to unpair Telegram user: ${res.statusText}`)
  return res.json()
}

export async function sendTelegramTestMessage(chatId: number): Promise<{ status: string; chat_id: number }> {
  const res = await fetch(`${API_BASE}/telegram/test-message?chat_id=${chatId}`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to send test message: ${res.statusText}`)
  return res.json()
}

export async function fetchSpeechStatus(): Promise<{
  status: string
  mode: string
  speech_enabled: boolean
  stt_status: string
  tts_status: string
  stt_engine: string
  tts_engine: string
  latency_ms: number
  last_heartbeat: string
}> {
  const res = await fetch(`${API_BASE}/speech/status`)
  if (!res.ok) throw new Error(`Failed to fetch speech status: ${res.statusText}`)
  return res.json()
}

export async function testSpeechPipeline(): Promise<{
  status: string
  mode: string
  latency_ms: number
  tested_at: string
  message: string
}> {
  const res = await fetch(`${API_BASE}/speech/test`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to test speech pipeline: ${res.statusText}`)
  return res.json()
}
