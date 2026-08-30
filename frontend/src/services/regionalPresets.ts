/** Shared regional market presets for OpenPrevue channel configuration. */

export interface RegionalPreset {
  label: string;
  metro: string;
  zip: string;
  lat: number;
  lon: number;
  radius: number;
  state: string;
}

export const REGIONAL_PRESETS: RegionalPreset[] = [
  { label: "NYC", metro: "NEW YORK CITY", zip: "10001", lat: 40.7128, lon: -74.0060, radius: 25, state: "NY" },
  { label: "LOS ANGELES", metro: "LOS ANGELES", zip: "90012", lat: 34.0522, lon: -118.2437, radius: 30, state: "CA" },
  { label: "CHICAGO", metro: "CHICAGO", zip: "60601", lat: 41.8781, lon: -87.6298, radius: 25, state: "IL" },
  { label: "ATLANTA", metro: "ATLANTA", zip: "30303", lat: 33.7490, lon: -84.3880, radius: 30, state: "GA" },
  { label: "NEW ORLEANS", metro: "NEW ORLEANS", zip: "70112", lat: 29.9511, lon: -90.0715, radius: 35, state: "LA" },
  { label: "DALLAS", metro: "DALLAS", zip: "75201", lat: 32.7767, lon: -96.7970, radius: 30, state: "TX" },
  { label: "AUSTIN", metro: "AUSTIN", zip: "78701", lat: 30.2672, lon: -97.7431, radius: 25, state: "TX" },
  { label: "MIAMI", metro: "MIAMI", zip: "33101", lat: 25.7617, lon: -80.1918, radius: 30, state: "FL" },
  { label: "ORLANDO", metro: "ORLANDO", zip: "32801", lat: 28.5383, lon: -81.3792, radius: 25, state: "FL" },
  { label: "TAMPA", metro: "TAMPA", zip: "33602", lat: 27.9506, lon: -82.4572, radius: 30, state: "FL" },
  { label: "SAN FRANCISCO", metro: "SAN FRANCISCO", zip: "94102", lat: 37.7749, lon: -122.4194, radius: 25, state: "CA" },
  { label: "LAS VEGAS", metro: "LAS VEGAS", zip: "89101", lat: 36.1699, lon: -115.1398, radius: 25, state: "NV" },
  { label: "PORTLAND", metro: "PORTLAND", zip: "97201", lat: 45.5152, lon: -122.6784, radius: 25, state: "OR" },
  { label: "SEATTLE", metro: "SEATTLE", zip: "98101", lat: 47.6062, lon: -122.3321, radius: 25, state: "WA" },
  { label: "LONDON", metro: "LONDON", zip: "EC1A 1BB", lat: 51.5074, lon: -0.1278, radius: 20, state: "UK" },
];
