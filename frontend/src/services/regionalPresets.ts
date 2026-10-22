/** Shared regional market presets for OpenPrevue channel configuration. */

export interface RegionalPreset {
  label: string;
  metro: string;
  zip: string;
  lat: number;
  lon: number;
  radius: number;
  state: string;
  timezone: string;
}

export const REGIONAL_PRESETS: RegionalPreset[] = [
  { label: "NYC", metro: "NEW YORK CITY", zip: "10001", lat: 40.7128, lon: -74.0060, radius: 25, state: "NY", timezone: "America/New_York" },
  { label: "LOS ANGELES", metro: "LOS ANGELES", zip: "90012", lat: 34.0522, lon: -118.2437, radius: 30, state: "CA", timezone: "America/Los_Angeles" },
  { label: "CHICAGO", metro: "CHICAGO", zip: "60601", lat: 41.8781, lon: -87.6298, radius: 25, state: "IL", timezone: "America/Chicago" },
  { label: "ATLANTA", metro: "ATLANTA", zip: "30303", lat: 33.7490, lon: -84.3880, radius: 30, state: "GA", timezone: "America/New_York" },
  { label: "NEW ORLEANS", metro: "NEW ORLEANS", zip: "70112", lat: 29.9511, lon: -90.0715, radius: 35, state: "LA", timezone: "America/Chicago" },
  { label: "DALLAS", metro: "DALLAS", zip: "75201", lat: 32.7767, lon: -96.7970, radius: 30, state: "TX", timezone: "America/Chicago" },
  { label: "AUSTIN", metro: "AUSTIN", zip: "78701", lat: 30.2672, lon: -97.7431, radius: 25, state: "TX", timezone: "America/Chicago" },
  { label: "MIAMI", metro: "MIAMI", zip: "33101", lat: 25.7617, lon: -80.1918, radius: 30, state: "FL", timezone: "America/New_York" },
  { label: "ORLANDO", metro: "ORLANDO", zip: "32801", lat: 28.5383, lon: -81.3792, radius: 25, state: "FL", timezone: "America/New_York" },
  { label: "TAMPA", metro: "TAMPA", zip: "33602", lat: 27.9506, lon: -82.4572, radius: 30, state: "FL", timezone: "America/New_York" },
  { label: "SAN FRANCISCO", metro: "SAN FRANCISCO", zip: "94102", lat: 37.7749, lon: -122.4194, radius: 25, state: "CA", timezone: "America/Los_Angeles" },
  { label: "LAS VEGAS", metro: "LAS VEGAS", zip: "89101", lat: 36.1699, lon: -115.1398, radius: 25, state: "NV", timezone: "America/Los_Angeles" },
  { label: "PORTLAND", metro: "PORTLAND", zip: "97201", lat: 45.5152, lon: -122.6784, radius: 25, state: "OR", timezone: "America/Los_Angeles" },
  { label: "SEATTLE", metro: "SEATTLE", zip: "98101", lat: 47.6062, lon: -122.3321, radius: 25, state: "WA", timezone: "America/Los_Angeles" },
  { label: "LONDON", metro: "LONDON", zip: "EC1A 1BB", lat: 51.5074, lon: -0.1278, radius: 20, state: "UK", timezone: "Europe/London" },
];
