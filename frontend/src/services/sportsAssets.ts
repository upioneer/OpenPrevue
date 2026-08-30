/** Vector sports league logos, team crests, and matchup parser for OpenPrevue. */

export interface TeamInfo {
  name: string;
  shortName: string;
  primaryColor: string;
  secondaryColor: string;
  logoSvg: string;
}

export interface MatchupInfo {
  isMatchup: boolean;
  league: string;
  homeTeam: TeamInfo;
  awayTeam: TeamInfo;
}

// Built-in SVG vector crests & helmets for turnkey offline homelab execution
const TEAM_REGISTRY: Record<string, TeamInfo> = {
  saints: {
    name: "New Orleans Saints",
    shortName: "NO",
    primaryColor: "#D3BC8D",
    secondaryColor: "#101820",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#D3BC8D] drop-shadow-md"><path d="M50 5 C55 25, 75 35, 90 40 C75 50, 70 70, 50 95 C30 70, 25 50, 10 40 C25 35, 45 25, 50 5 Z"/></svg>`
  },
  falcons: {
    name: "Atlanta Falcons",
    shortName: "ATL",
    primaryColor: "#A71930",
    secondaryColor: "#000000",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#A71930] drop-shadow-md"><polygon points="20,10 80,10 90,40 50,90 40,60 70,40 40,30 20,60"/></svg>`
  },
  pelicans: {
    name: "New Orleans Pelicans",
    shortName: "NOP",
    primaryColor: "#0C2340",
    secondaryColor: "#C8102E",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#C8102E] drop-shadow-md"><circle cx="50" cy="50" r="40"/><path d="M25 50 Q50 20 75 50 Q50 80 25 50" fill="#D3BC8D"/></svg>`
  },
  lakers: {
    name: "Los Angeles Lakers",
    shortName: "LAL",
    primaryColor: "#552583",
    secondaryColor: "#FDB927",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#FDB927] drop-shadow-md"><circle cx="50" cy="50" r="42" fill="#552583"/><text x="50" y="58" font-size="22" font-family="monospace" font-weight="900" text-anchor="middle" fill="#FDB927">LAL</text></svg>`
  },
  warriors: {
    name: "Golden State Warriors",
    shortName: "GSW",
    primaryColor: "#1D428A",
    secondaryColor: "#FFC72C",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#FFC72C] drop-shadow-md"><circle cx="50" cy="50" r="42" fill="#1D428A"/><path d="M30 70 Q50 30 70 70" stroke="#FFC72C" stroke-width="8" fill="none"/></svg>`
  },
  astros: {
    name: "Houston Astros",
    shortName: "HOU",
    primaryColor: "#002D62",
    secondaryColor: "#EB6E1F",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#EB6E1F] drop-shadow-md"><polygon points="50,10 62,38 92,38 68,56 77,84 50,67 23,84 32,56 8,38 38,38" fill="#EB6E1F"/><text x="50" y="62" font-size="26" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="#002D62">H</text></svg>`
  },
  rangers: {
    name: "Texas Rangers",
    shortName: "TEX",
    primaryColor: "#003278",
    secondaryColor: "#C0111F",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#C0111F] drop-shadow-md"><rect x="15" y="15" width="70" height="70" rx="8" fill="#003278"/><text x="50" y="68" font-size="48" font-family="serif" font-weight="bold" text-anchor="middle" fill="#FFFFFF">T</text></svg>`
  },
  dynamo: {
    name: "Houston Dynamo FC",
    shortName: "HOU",
    primaryColor: "#F4911E",
    secondaryColor: "#101820",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#F4911E] drop-shadow-md"><polygon points="50,10 85,30 85,70 50,90 15,70 15,30" fill="#101820" stroke="#F4911E" stroke-width="6"/><text x="50" y="60" font-size="28" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="#F4911E">HD</text></svg>`
  },
  austin: {
    name: "Austin FC",
    shortName: "ATX",
    primaryColor: "#00B140",
    secondaryColor: "#000000",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#00B140] drop-shadow-md"><rect x="15" y="15" width="70" height="70" rx="6" fill="#000000" stroke="#00B140" stroke-width="6"/><text x="50" y="60" font-size="24" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="#00B140">ATX</text></svg>`
  },
  f1: {
    name: "Formula 1",
    shortName: "F1",
    primaryColor: "#E10600",
    secondaryColor: "#FFFFFF",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#E10600] drop-shadow-md"><text x="50" y="62" font-size="44" font-family="sans-serif" font-style="italic" font-weight="900" text-anchor="middle" fill="#E10600">F1</text></svg>`
  },
  nascar: {
    name: "NASCAR Cup Series",
    shortName: "NASCAR",
    primaryColor: "#007AC2",
    secondaryColor: "#FFD100",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current drop-shadow-md"><rect x="10" y="30" width="80" height="40" rx="4" fill="#007AC2"/><polygon points="20,70 30,30 50,30 40,70" fill="#FFD100"/><text x="62" y="58" font-size="18" font-family="sans-serif" font-style="italic" font-weight="bold" fill="#FFFFFF">CUP</text></svg>`
  },
  indycar: {
    name: "NTT IndyCar Series",
    shortName: "INDY",
    primaryColor: "#E31B23",
    secondaryColor: "#000000",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current drop-shadow-md"><circle cx="50" cy="50" r="42" fill="#E31B23"/><text x="50" y="58" font-size="18" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="#FFFFFF">INDY</text></svg>`
  },
  motogp: {
    name: "FIM MotoGP",
    shortName: "MOTOGP",
    primaryColor: "#D6001C",
    secondaryColor: "#000000",
    logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current drop-shadow-md"><circle cx="50" cy="50" r="42" fill="#111111" stroke="#D6001C" stroke-width="6"/><text x="50" y="58" font-size="16" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="#D6001C">MOTO</text></svg>`
  }
};

export function parseSportsMatchup(title: string): MatchupInfo | null {
  const upper = title.toUpperCase();

  // Detect League
  let league = "SPORTS";
  if (upper.includes("NFL:") || upper.includes("SAINTS") || upper.includes("FALCONS")) league = "NFL";
  else if (upper.includes("NBA:") || upper.includes("PELICANS") || upper.includes("LAKERS") || upper.includes("WARRIORS")) league = "NBA";
  else if (upper.includes("MLB:") || upper.includes("ASTROS") || upper.includes("RANGERS")) league = "MLB";
  else if (upper.includes("MLS:") || upper.includes("DYNAMO") || upper.includes("AUSTIN FC")) league = "MLS";
  else if (upper.includes("FORMULA 1") || upper.includes("GRAND PRIX") || upper.includes("F1")) league = "FORMULA 1";
  else if (upper.includes("NASCAR")) league = "NASCAR";
  else if (upper.includes("INDYCAR")) league = "INDYCAR";
  else if (upper.includes("MOTOGP")) league = "MOTOGP";

  // Check for VS pattern
  if (upper.includes(" VS ") || upper.includes(" @ ")) {
    const parts = upper.split(/ VS | @ /);
    if (parts.length >= 2) {
      const awayRaw = parts[0].replace(/NFL:|NBA:|MLB:|MLS:|LIVE NATION PRESENTS:|VIVID SEATS:/gi, "").trim().toLowerCase();
      const homeRaw = parts[1].trim().toLowerCase();

      const awayKey = Object.keys(TEAM_REGISTRY).find(k => awayRaw.includes(k)) || "f1";
      const homeKey = Object.keys(TEAM_REGISTRY).find(k => homeRaw.includes(k)) || "saints";

      return {
        isMatchup: true,
        league,
        awayTeam: TEAM_REGISTRY[awayKey] || {
          name: parts[0].trim(),
          shortName: "AWAY",
          primaryColor: "#00FFFF",
          secondaryColor: "#000033",
          logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#00FFFF]"><circle cx="50" cy="50" r="40"/><text x="50" y="60" font-size="28" font-family="monospace" text-anchor="middle" fill="#000033">AWY</text></svg>`
        },
        homeTeam: TEAM_REGISTRY[homeKey] || {
          name: parts[1].trim(),
          shortName: "HOME",
          primaryColor: "#FFFF00",
          secondaryColor: "#000033",
          logoSvg: `<svg viewBox="0 0 100 100" class="w-full h-full fill-current text-[#FFFF00]"><circle cx="50" cy="50" r="40"/><text x="50" y="60" font-size="28" font-family="monospace" text-anchor="middle" fill="#000033">HOM</text></svg>`
        }
      };
    }
  }

  // Single Motorsport Event (F1, NASCAR, IndyCar, MotoGP)
  if (league === "FORMULA 1" || league === "NASCAR" || league === "INDYCAR" || league === "MOTOGP") {
    const motorKey = league === "FORMULA 1" ? "f1" : league.toLowerCase();
    const info = TEAM_REGISTRY[motorKey] || TEAM_REGISTRY["f1"];
    return {
      isMatchup: false,
      league,
      homeTeam: info,
      awayTeam: info
    };
  }

  return null;
}
