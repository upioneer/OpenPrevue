/**
 * Sports team branding, official franchise colors, acronyms, and CDN logo resolver.
 */

export interface TeamBranding {
  name: string
  shortName: string
  primaryColor: string
  secondaryColor: string
  textColor: string
  logoUrl?: string
}

export interface ParsedMatchup {
  teamA: string
  teamB: string
  league?: string
}

const TEAMS_DATABASE: Record<string, TeamBranding> = {
  // NBA Teams
  'new york knicks': {
    name: 'New York Knicks',
    shortName: 'NYK',
    primaryColor: '#006BB6',
    secondaryColor: '#F58426',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/nyk.png',
  },
  'knicks': {
    name: 'New York Knicks',
    shortName: 'NYK',
    primaryColor: '#006BB6',
    secondaryColor: '#F58426',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/nyk.png',
  },
  'boston celtics': {
    name: 'Boston Celtics',
    shortName: 'BOS',
    primaryColor: '#007A33',
    secondaryColor: '#BA9653',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/bos.png',
  },
  'celtics': {
    name: 'Boston Celtics',
    shortName: 'BOS',
    primaryColor: '#007A33',
    secondaryColor: '#BA9653',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/bos.png',
  },
  'brooklyn nets': {
    name: 'Brooklyn Nets',
    shortName: 'BKN',
    primaryColor: '#000000',
    secondaryColor: '#FFFFFF',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/bkn.png',
  },
  'nets': {
    name: 'Brooklyn Nets',
    shortName: 'BKN',
    primaryColor: '#000000',
    secondaryColor: '#FFFFFF',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/bkn.png',
  },
  'miami heat': {
    name: 'Miami Heat',
    shortName: 'MIA',
    primaryColor: '#98002E',
    secondaryColor: '#F9A01B',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/mia.png',
  },
  'heat': {
    name: 'Miami Heat',
    shortName: 'MIA',
    primaryColor: '#98002E',
    secondaryColor: '#F9A01B',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/mia.png',
  },
  'new orleans pelicans': {
    name: 'New Orleans Pelicans',
    shortName: 'NOP',
    primaryColor: '#0C2340',
    secondaryColor: '#C8102E',
    textColor: '#E5A823',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/no.png',
  },
  'pelicans': {
    name: 'New Orleans Pelicans',
    shortName: 'NOP',
    primaryColor: '#0C2340',
    secondaryColor: '#C8102E',
    textColor: '#E5A823',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/no.png',
  },
  'los angeles lakers': {
    name: 'Los Angeles Lakers',
    shortName: 'LAL',
    primaryColor: '#552583',
    secondaryColor: '#FDB927',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/lal.png',
  },
  'lakers': {
    name: 'Los Angeles Lakers',
    shortName: 'LAL',
    primaryColor: '#552583',
    secondaryColor: '#FDB927',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/lal.png',
  },
  'golden state warriors': {
    name: 'Golden State Warriors',
    shortName: 'GSW',
    primaryColor: '#1D428A',
    secondaryColor: '#FFC72C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/gsw.png',
  },
  'warriors': {
    name: 'Golden State Warriors',
    shortName: 'GSW',
    primaryColor: '#1D428A',
    secondaryColor: '#FFC72C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/gsw.png',
  },
  'chicago bulls': {
    name: 'Chicago Bulls',
    shortName: 'CHI',
    primaryColor: '#CE1141',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/chi.png',
  },
  'bulls': {
    name: 'Chicago Bulls',
    shortName: 'CHI',
    primaryColor: '#CE1141',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/chi.png',
  },
  'philadelphia 76ers': {
    name: 'Philadelphia 76ers',
    shortName: 'PHI',
    primaryColor: '#006BB6',
    secondaryColor: '#ED174C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/phi.png',
  },
  '76ers': {
    name: 'Philadelphia 76ers',
    shortName: 'PHI',
    primaryColor: '#006BB6',
    secondaryColor: '#ED174C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/phi.png',
  },
  'dallas mavericks': {
    name: 'Dallas Mavericks',
    shortName: 'DAL',
    primaryColor: '#00538C',
    secondaryColor: '#002B5E',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/dal.png',
  },
  'mavericks': {
    name: 'Dallas Mavericks',
    shortName: 'DAL',
    primaryColor: '#00538C',
    secondaryColor: '#002B5E',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/dal.png',
  },
  'san antonio spurs': {
    name: 'San Antonio Spurs',
    shortName: 'SAS',
    primaryColor: '#C4CED4',
    secondaryColor: '#000000',
    textColor: '#000000',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/sa.png',
  },
  'spurs': {
    name: 'San Antonio Spurs',
    shortName: 'SAS',
    primaryColor: '#C4CED4',
    secondaryColor: '#000000',
    textColor: '#000000',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/sa.png',
  },
  'houston rockets': {
    name: 'Houston Rockets',
    shortName: 'HOU',
    primaryColor: '#CE1141',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/hou.png',
  },
  'rockets': {
    name: 'Houston Rockets',
    shortName: 'HOU',
    primaryColor: '#CE1141',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nba/500/hou.png',
  },

  // NFL Teams
  'new orleans saints': {
    name: 'New Orleans Saints',
    shortName: 'NO',
    primaryColor: '#D3BC8D',
    secondaryColor: '#101820',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png',
  },
  'saints': {
    name: 'New Orleans Saints',
    shortName: 'NO',
    primaryColor: '#D3BC8D',
    secondaryColor: '#101820',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png',
  },
  'atlanta falcons': {
    name: 'Atlanta Falcons',
    shortName: 'ATL',
    primaryColor: '#A71930',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png',
  },
  'falcons': {
    name: 'Atlanta Falcons',
    shortName: 'ATL',
    primaryColor: '#A71930',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png',
  },
  'new york giants': {
    name: 'New York Giants',
    shortName: 'NYG',
    primaryColor: '#0B2265',
    secondaryColor: '#A71930',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png',
  },
  'giants': {
    name: 'New York Giants',
    shortName: 'NYG',
    primaryColor: '#0B2265',
    secondaryColor: '#A71930',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png',
  },
  'new york jets': {
    name: 'New York Jets',
    shortName: 'NYJ',
    primaryColor: '#125740',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
  },
  'jets': {
    name: 'New York Jets',
    shortName: 'NYJ',
    primaryColor: '#125740',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
  },
  'dallas cowboys': {
    name: 'Dallas Cowboys',
    shortName: 'DAL',
    primaryColor: '#003594',
    secondaryColor: '#041E42',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png',
  },
  'cowboys': {
    name: 'Dallas Cowboys',
    shortName: 'DAL',
    primaryColor: '#003594',
    secondaryColor: '#041E42',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png',
  },
  'philadelphia eagles': {
    name: 'Philadelphia Eagles',
    shortName: 'PHI',
    primaryColor: '#004C54',
    secondaryColor: '#A5ACAF',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png',
  },
  'eagles': {
    name: 'Philadelphia Eagles',
    shortName: 'PHI',
    primaryColor: '#004C54',
    secondaryColor: '#A5ACAF',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png',
  },
  'kansas city chiefs': {
    name: 'Kansas City Chiefs',
    shortName: 'KC',
    primaryColor: '#E31837',
    secondaryColor: '#FFB81C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png',
  },
  'chiefs': {
    name: 'Kansas City Chiefs',
    shortName: 'KC',
    primaryColor: '#E31837',
    secondaryColor: '#FFB81C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png',
  },
  'houston texans': {
    name: 'Houston Texans',
    shortName: 'HOU',
    primaryColor: '#03202F',
    secondaryColor: '#A71930',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png',
  },
  'texans': {
    name: 'Houston Texans',
    shortName: 'HOU',
    primaryColor: '#03202F',
    secondaryColor: '#A71930',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png',
  },

  // MLB Teams
  'new york yankees': {
    name: 'New York Yankees',
    shortName: 'NYY',
    primaryColor: '#003087',
    secondaryColor: '#E4002C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png',
  },
  'yankees': {
    name: 'New York Yankees',
    shortName: 'NYY',
    primaryColor: '#003087',
    secondaryColor: '#E4002C',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png',
  },
  'new york mets': {
    name: 'New York Mets',
    shortName: 'NYM',
    primaryColor: '#002D72',
    secondaryColor: '#FF5910',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/nym.png',
  },
  'mets': {
    name: 'New York Mets',
    shortName: 'NYM',
    primaryColor: '#002D72',
    secondaryColor: '#FF5910',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/nym.png',
  },
  'houston astros': {
    name: 'Houston Astros',
    shortName: 'HOU',
    primaryColor: '#002D62',
    secondaryColor: '#EB6E1F',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/hou.png',
  },
  'astros': {
    name: 'Houston Astros',
    shortName: 'HOU',
    primaryColor: '#002D62',
    secondaryColor: '#EB6E1F',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/hou.png',
  },
  'texas rangers': {
    name: 'Texas Rangers',
    shortName: 'TEX',
    primaryColor: '#003278',
    secondaryColor: '#C0111F',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/tex.png',
  },
  'rangers': {
    name: 'Texas Rangers',
    shortName: 'TEX',
    primaryColor: '#003278',
    secondaryColor: '#C0111F',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/tex.png',
  },
  'boston red sox': {
    name: 'Boston Red Sox',
    shortName: 'BOS',
    primaryColor: '#BD3039',
    secondaryColor: '#0C2340',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/bos.png',
  },
  'red sox': {
    name: 'Boston Red Sox',
    shortName: 'BOS',
    primaryColor: '#BD3039',
    secondaryColor: '#0C2340',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/mlb/500/bos.png',
  },

  // MLS Teams
  'houston dynamo fc': {
    name: 'Houston Dynamo FC',
    shortName: 'HOU',
    primaryColor: '#FF6600',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/soccer/500/118.png',
  },
  'houston dynamo': {
    name: 'Houston Dynamo FC',
    shortName: 'HOU',
    primaryColor: '#FF6600',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/soccer/500/118.png',
  },
  'austin fc': {
    name: 'Austin FC',
    shortName: 'ATX',
    primaryColor: '#00B140',
    secondaryColor: '#000000',
    textColor: '#FFFFFF',
    logoUrl: 'https://a.espncdn.com/i/teamlogos/soccer/500/20906.png',
  },
}

/**
 * Robust case-insensitive sports title parser that splits matchup pairs and extracts league prefixes.
 */
export function parseMatchup(rawTitle: string): ParsedMatchup | null {
  if (!rawTitle) return null

  let league: string | undefined
  const leagueMatch = rawTitle.match(/^(nba|nfl|mlb|mls|nhl|wnba|nascar|indycar|motogp|formula 1|f1):\s*/i)
  if (leagueMatch) {
    league = leagueMatch[1].toUpperCase()
  }

  const title = rawTitle.replace(/^(nba|nfl|mlb|mls|nhl|wnba|nascar|indycar|motogp|formula 1|f1):\s*/i, '').trim()

  // Match VS variations case-insensitively
  if (/\s+(?:vs\.?|against|v)\s+/i.test(title)) {
    const parts = title.split(/\s+(?:vs\.?|against|v)\s+/i)
    if (parts.length >= 2) {
      return { teamA: parts[0].trim(), teamB: parts[1].trim(), league }
    }
  }

  // Match @ variations (Away @ Home)
  if (/\s+@\s+/i.test(title)) {
    const parts = title.split(/\s+@\s+/i)
    if (parts.length >= 2) {
      return { teamA: parts[1].trim(), teamB: parts[0].trim(), league }
    }
  }

  return null
}

/**
 * Resolve team branding details from team name string with fuzzy matching and dynamic fallback.
 */
export function resolveTeamBranding(rawName: string): TeamBranding {
  if (!rawName) {
    return {
      name: 'TEAM',
      shortName: 'TBD',
      primaryColor: '#000066',
      secondaryColor: '#FFFF00',
      textColor: '#FFFFFF',
    }
  }

  const clean = rawName.trim().toLowerCase().replace(/^(the|nba:|nfl:|mlb:|mls:)\s+/i, '')

  if (TEAMS_DATABASE[clean]) {
    return TEAMS_DATABASE[clean]
  }

  // Partial match check
  for (const [key, value] of Object.entries(TEAMS_DATABASE)) {
    if (clean.includes(key) || key.includes(clean)) {
      return value
    }
  }

  // Dynamic fallback palette generation based on string hash
  let hash = 0
  for (let i = 0; i < rawName.length; i++) {
    hash = rawName.charCodeAt(i) + ((hash << 5) - hash)
  }
  const hue = Math.abs(hash % 360)
  const primary = `hsl(${hue}, 75%, 45%)`
  const secondary = `hsl(${(hue + 45) % 360}, 85%, 55%)`

  const words = rawName.trim().split(/\s+/)
  const short = words.length >= 2
    ? (words[0][0] + words[1][0] + (words[2] ? words[2][0] : '')).toUpperCase()
    : rawName.slice(0, 3).toUpperCase()

  return {
    name: rawName,
    shortName: short,
    primaryColor: primary,
    secondaryColor: secondary,
    textColor: '#FFFFFF',
  }
}
