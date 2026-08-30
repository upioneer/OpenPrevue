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
