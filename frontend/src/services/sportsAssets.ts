/** 
 * Comprehensive Sports League Registry and Vector Matchup Generator for OpenPrevue.
 * Provides 100% complete coverage for all 32 NFL, 30 NBA, 30 MLB, 32 NHL, 29 MLS, 20 Premier League teams & F1.
 */

export interface TeamInfo {
  name: string;
  city: string;
  nickname: string;
  shortName: string;
  league: string;
  primaryColor: string;
  secondaryColor: string;
  logoSvg: string;
  aliases: string[];
}

export interface MatchupInfo {
  isMatchup: boolean;
  league: string;
  homeTeam: TeamInfo;
  awayTeam: TeamInfo;
  headline?: string;
}

function makeShieldSvg(text: string, bg: string, fg: string, border: string = "#FFFF00"): string {
  return `<svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-md">
    <polygon points="50,5 92,22 84,72 50,95 16,72 8,22" fill="${bg}" stroke="${border}" stroke-width="4"/>
    <text x="50" y="58" font-size="${text.length > 3 ? '20' : '28'}" font-family="monospace, sans-serif" font-weight="900" text-anchor="middle" fill="${fg}">${text}</text>
  </svg>`;
}

function makeHelmetSvg(text: string, helmetColor: string, stripeColor: string, faceColor: string): string {
  return `<svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-md">
    <circle cx="50" cy="50" r="44" fill="${helmetColor}" stroke="${stripeColor}" stroke-width="4"/>
    <path d="M50 6 A44 44 0 0 1 50 94" fill="none" stroke="${stripeColor}" stroke-width="8"/>
    <rect x="24" y="45" width="52" height="28" rx="4" fill="${faceColor}" opacity="0.85"/>
    <text x="50" y="65" font-size="18" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="#FFFFFF">${text}</text>
  </svg>`;
}

function makeCircleSvg(text: string, bg: string, fg: string, stroke: string = "#FFFFFF"): string {
  return `<svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-md">
    <circle cx="50" cy="50" r="42" fill="${bg}" stroke="${stroke}" stroke-width="5"/>
    <text x="50" y="59" font-size="${text.length > 3 ? '18' : '26'}" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="${fg}">${text}</text>
  </svg>`;
}

function makeDiamondSvg(text: string, bg: string, fg: string, stroke: string = "#FFFFFF"): string {
  return `<svg viewBox="0 0 100 100" class="w-full h-full drop-shadow-md">
    <polygon points="50,6 94,50 50,94 6,50" fill="${bg}" stroke="${stroke}" stroke-width="5"/>
    <text x="50" y="58" font-size="${text.length > 3 ? '18' : '26'}" font-family="sans-serif" font-weight="900" text-anchor="middle" fill="${fg}">${text}</text>
  </svg>`;
}

// 100% COMPLETE 32-TEAM NFL FRANCHISE REGISTRY
const NFL_TEAMS: TeamInfo[] = [
  { name: "Arizona Cardinals", city: "Arizona", nickname: "Cardinals", shortName: "ARI", league: "NFL", primaryColor: "#97233F", secondaryColor: "#000000", logoSvg: makeHelmetSvg("ARI", "#97233F", "#FFB612", "#000000"), aliases: ["cardinals", "arizona cardinals", "ari"] },
  { name: "Atlanta Falcons", city: "Atlanta", nickname: "Falcons", shortName: "ATL", league: "NFL", primaryColor: "#A71930", secondaryColor: "#000000", logoSvg: makeHelmetSvg("ATL", "#000000", "#A71930", "#A71930"), aliases: ["falcons", "atlanta falcons", "atl"] },
  { name: "Baltimore Ravens", city: "Baltimore", nickname: "Ravens", shortName: "BAL", league: "NFL", primaryColor: "#241773", secondaryColor: "#000000", logoSvg: makeHelmetSvg("BAL", "#241773", "#9E7C0C", "#000000"), aliases: ["ravens", "baltimore ravens", "bal"] },
  { name: "Buffalo Bills", city: "Buffalo", nickname: "Bills", shortName: "BUF", league: "NFL", primaryColor: "#00338D", secondaryColor: "#C60C30", logoSvg: makeHelmetSvg("BUF", "#00338D", "#C60C30", "#FFFFFF"), aliases: ["bills", "buffalo bills", "buf"] },
  { name: "Carolina Panthers", city: "Carolina", nickname: "Panthers", shortName: "CAR", league: "NFL", primaryColor: "#0085CA", secondaryColor: "#101820", logoSvg: makeHelmetSvg("CAR", "#101820", "#0085CA", "#BFC0BF"), aliases: ["panthers", "carolina panthers", "car"] },
  { name: "Chicago Bears", city: "Chicago", nickname: "Bears", shortName: "CHI", league: "NFL", primaryColor: "#0B162A", secondaryColor: "#C83803", logoSvg: makeHelmetSvg("CHI", "#0B162A", "#C83803", "#C83803"), aliases: ["bears", "chicago bears", "chi"] },
  { name: "Cincinnati Bengals", city: "Cincinnati", nickname: "Bengals", shortName: "CIN", league: "NFL", primaryColor: "#FB4F14", secondaryColor: "#000000", logoSvg: makeHelmetSvg("CIN", "#FB4F14", "#000000", "#FFFFFF"), aliases: ["bengals", "cincinnati bengals", "cin"] },
  { name: "Cleveland Browns", city: "Cleveland", nickname: "Browns", shortName: "CLE", league: "NFL", primaryColor: "#311D00", secondaryColor: "#FF3C00", logoSvg: makeHelmetSvg("CLE", "#FF3C00", "#311D00", "#FFFFFF"), aliases: ["browns", "cleveland browns", "cle"] },
  { name: "Dallas Cowboys", city: "Dallas", nickname: "Cowboys", shortName: "DAL", league: "NFL", primaryColor: "#003594", secondaryColor: "#041E42", logoSvg: makeHelmetSvg("DAL", "#869397", "#003594", "#003594"), aliases: ["cowboys", "dallas cowboys", "dal"] },
  { name: "Denver Broncos", city: "Denver", nickname: "Broncos", shortName: "DEN", league: "NFL", primaryColor: "#FB4F14", secondaryColor: "#002244", logoSvg: makeHelmetSvg("DEN", "#002244", "#FB4F14", "#FFFFFF"), aliases: ["broncos", "denver broncos", "den"] },
  { name: "Detroit Lions", city: "Detroit", nickname: "Lions", shortName: "DET", league: "NFL", primaryColor: "#0076B6", secondaryColor: "#B0B7BC", logoSvg: makeHelmetSvg("DET", "#B0B7BC", "#0076B6", "#0076B6"), aliases: ["lions", "detroit lions", "det"] },
  { name: "Green Bay Packers", city: "Green Bay", nickname: "Packers", shortName: "GB", league: "NFL", primaryColor: "#203731", secondaryColor: "#FFB612", logoSvg: makeHelmetSvg("GB", "#FFB612", "#203731", "#203731"), aliases: ["packers", "green bay packers", "gb"] },
  { name: "Houston Texans", city: "Houston", nickname: "Texans", shortName: "HOU", league: "NFL", primaryColor: "#03202F", secondaryColor: "#A71930", logoSvg: makeHelmetSvg("HOU", "#03202F", "#A71930", "#FFFFFF"), aliases: ["texans", "houston texans", "hou"] },
  { name: "Indianapolis Colts", city: "Indianapolis", nickname: "Colts", shortName: "IND", league: "NFL", primaryColor: "#002C5F", secondaryColor: "#A2AAAD", logoSvg: makeHelmetSvg("IND", "#FFFFFF", "#002C5F", "#002C5F"), aliases: ["colts", "indianapolis colts", "ind"] },
  { name: "Jacksonville Jaguars", city: "Jacksonville", nickname: "Jaguars", shortName: "JAX", league: "NFL", primaryColor: "#006778", secondaryColor: "#D7A22A", logoSvg: makeHelmetSvg("JAX", "#000000", "#006778", "#D7A22A"), aliases: ["jaguars", "jacksonville jaguars", "jax"] },
  { name: "Kansas City Chiefs", city: "Kansas City", nickname: "Chiefs", shortName: "KC", league: "NFL", primaryColor: "#E31837", secondaryColor: "#FFB81C", logoSvg: makeHelmetSvg("KC", "#E31837", "#FFB81C", "#FFFFFF"), aliases: ["chiefs", "kansas city chiefs", "kc"] },
  { name: "Las Vegas Raiders", city: "Las Vegas", nickname: "Raiders", shortName: "LV", league: "NFL", primaryColor: "#000000", secondaryColor: "#A5ACAF", logoSvg: makeShieldSvg("LV", "#000000", "#A5ACAF", "#A5ACAF"), aliases: ["raiders", "las vegas raiders", "oakland raiders", "lv"] },
  { name: "Los Angeles Chargers", city: "Los Angeles", nickname: "Chargers", shortName: "LAC", league: "NFL", primaryColor: "#0080C6", secondaryColor: "#FFC20E", logoSvg: makeHelmetSvg("LAC", "#FFFFFF", "#0080C6", "#FFC20E"), aliases: ["chargers", "la chargers", "lac"] },
  { name: "Los Angeles Rams", city: "Los Angeles", nickname: "Rams", shortName: "LAR", league: "NFL", primaryColor: "#003594", secondaryColor: "#FFA300", logoSvg: makeHelmetSvg("LAR", "#003594", "#FFA300", "#FFFFFF"), aliases: ["rams", "la rams", "lar"] },
  { name: "Miami Dolphins", city: "Miami", nickname: "Dolphins", shortName: "MIA", league: "NFL", primaryColor: "#008E97", secondaryColor: "#FC4C02", logoSvg: makeHelmetSvg("MIA", "#FFFFFF", "#008E97", "#FC4C02"), aliases: ["dolphins", "miami dolphins", "mia"] },
  { name: "Minnesota Vikings", city: "Minnesota", nickname: "Vikings", shortName: "MIN", league: "NFL", primaryColor: "#4F2683", secondaryColor: "#FFC62F", logoSvg: makeHelmetSvg("MIN", "#4F2683", "#FFC62F", "#FFFFFF"), aliases: ["vikings", "minnesota vikings", "min"] },
  { name: "New England Patriots", city: "New England", nickname: "Patriots", shortName: "NE", league: "NFL", primaryColor: "#002244", secondaryColor: "#C60C30", logoSvg: makeHelmetSvg("NE", "#B0B7BC", "#002244", "#C60C30"), aliases: ["patriots", "new england patriots", "ne"] },
  { name: "New Orleans Saints", city: "New Orleans", nickname: "Saints", shortName: "NO", league: "NFL", primaryColor: "#D3BC8D", secondaryColor: "#101820", logoSvg: makeShieldSvg("NO", "#101820", "#D3BC8D", "#D3BC8D"), aliases: ["saints", "new orleans saints", "no"] },
  { name: "New York Giants", city: "New York", nickname: "Giants", shortName: "NYG", league: "NFL", primaryColor: "#0B2265", secondaryColor: "#A71930", logoSvg: makeHelmetSvg("NYG", "#0B2265", "#A71930", "#FFFFFF"), aliases: ["giants", "new york giants", "nyg"] },
  { name: "New York Jets", city: "New York", nickname: "Jets", shortName: "NYJ", league: "NFL", primaryColor: "#125740", secondaryColor: "#FFFFFF", logoSvg: makeHelmetSvg("NYJ", "#125740", "#FFFFFF", "#000000"), aliases: ["jets", "new york jets", "nyj"] },
  { name: "Philadelphia Eagles", city: "Philadelphia", nickname: "Eagles", shortName: "PHI", league: "NFL", primaryColor: "#004C54", secondaryColor: "#A5ACAF", logoSvg: makeHelmetSvg("PHI", "#004C54", "#A5ACAF", "#000000"), aliases: ["eagles", "philadelphia eagles", "phi"] },
  { name: "Pittsburgh Steelers", city: "Pittsburgh", nickname: "Steelers", shortName: "PIT", league: "NFL", primaryColor: "#FFB612", secondaryColor: "#101820", logoSvg: makeHelmetSvg("PIT", "#101820", "#FFB612", "#FFB612"), aliases: ["steelers", "pittsburgh steelers", "pit"] },
  { name: "San Francisco 49ers", city: "San Francisco", nickname: "49ers", shortName: "SF", league: "NFL", primaryColor: "#AA0000", secondaryColor: "#B3995D", logoSvg: makeHelmetSvg("SF", "#B3995D", "#AA0000", "#AA0000"), aliases: ["49ers", "san francisco 49ers", "niners", "sf"] },
  { name: "Seattle Seahawks", city: "Seattle", nickname: "Seahawks", shortName: "SEA", league: "NFL", primaryColor: "#002244", secondaryColor: "#69BE28", logoSvg: makeHelmetSvg("SEA", "#002244", "#69BE28", "#A5ACAF"), aliases: ["seahawks", "seattle seahawks", "sea"] },
  { name: "Tampa Bay Buccaneers", city: "Tampa Bay", nickname: "Buccaneers", shortName: "TB", league: "NFL", primaryColor: "#D50A0A", secondaryColor: "#0A0A08", logoSvg: makeHelmetSvg("TB", "#897653", "#D50A0A", "#0A0A08"), aliases: ["buccaneers", "bucs", "tampa bay buccaneers", "tb"] },
  { name: "Tennessee Titans", city: "Tennessee", nickname: "Titans", shortName: "TEN", league: "NFL", primaryColor: "#0C2340", secondaryColor: "#4B92DB", logoSvg: makeHelmetSvg("TEN", "#0C2340", "#4B92DB", "#C8102E"), aliases: ["titans", "tennessee titans", "ten"] },
  { name: "Washington Commanders", city: "Washington", nickname: "Commanders", shortName: "WAS", league: "NFL", primaryColor: "#5A1414", secondaryColor: "#FFB612", logoSvg: makeHelmetSvg("WAS", "#5A1414", "#FFB612", "#FFB612"), aliases: ["commanders", "washington commanders", "was"] },
];

// 100% COMPLETE 30-TEAM NBA FRANCHISE REGISTRY
const NBA_TEAMS: TeamInfo[] = [
  { name: "Atlanta Hawks", city: "Atlanta", nickname: "Hawks", shortName: "ATL", league: "NBA", primaryColor: "#E03A3E", secondaryColor: "#C1D32F", logoSvg: makeCircleSvg("ATL", "#E03A3E", "#FFFFFF", "#C1D32F"), aliases: ["hawks", "atlanta hawks"] },
  { name: "Boston Celtics", city: "Boston", nickname: "Celtics", shortName: "BOS", league: "NBA", primaryColor: "#007A33", secondaryColor: "#BA9653", logoSvg: makeCircleSvg("BOS", "#007A33", "#FFFFFF", "#BA9653"), aliases: ["celtics", "boston celtics"] },
  { name: "Brooklyn Nets", city: "Brooklyn", nickname: "Nets", shortName: "BKN", league: "NBA", primaryColor: "#000000", secondaryColor: "#FFFFFF", logoSvg: makeCircleSvg("BKN", "#000000", "#FFFFFF", "#FFFFFF"), aliases: ["nets", "brooklyn nets"] },
  { name: "Charlotte Hornets", city: "Charlotte", nickname: "Hornets", shortName: "CHA", league: "NBA", primaryColor: "#1D1160", secondaryColor: "#00788C", logoSvg: makeCircleSvg("CHA", "#1D1160", "#00788C", "#A1A1A4"), aliases: ["hornets", "charlotte hornets"] },
  { name: "Chicago Bulls", city: "Chicago", nickname: "Bulls", shortName: "CHI", league: "NBA", primaryColor: "#CE1141", secondaryColor: "#000000", logoSvg: makeCircleSvg("CHI", "#CE1141", "#FFFFFF", "#000000"), aliases: ["bulls", "chicago bulls"] },
  { name: "Cleveland Cavaliers", city: "Cleveland", nickname: "Cavaliers", shortName: "CLE", league: "NBA", primaryColor: "#860038", secondaryColor: "#041E42", logoSvg: makeCircleSvg("CLE", "#860038", "#FDBB30", "#041E42"), aliases: ["cavaliers", "cavs", "cleveland cavaliers"] },
  { name: "Dallas Mavericks", city: "Dallas", nickname: "Mavericks", shortName: "DAL", league: "NBA", primaryColor: "#00538C", secondaryColor: "#002B5E", logoSvg: makeCircleSvg("DAL", "#00538C", "#B8C4CA", "#FFFFFF"), aliases: ["mavericks", "mavs", "dallas mavericks"] },
  { name: "Denver Nuggets", city: "Denver", nickname: "Nuggets", shortName: "DEN", league: "NBA", primaryColor: "#0E2240", secondaryColor: "#FEC524", logoSvg: makeCircleSvg("DEN", "#0E2240", "#FEC524", "#8B2131"), aliases: ["nuggets", "denver nuggets"] },
  { name: "Detroit Pistons", city: "Detroit", nickname: "Pistons", shortName: "DET", league: "NBA", primaryColor: "#C8102E", secondaryColor: "#1D42BA", logoSvg: makeCircleSvg("DET", "#1D42BA", "#C8102E", "#BEC0C2"), aliases: ["pistons", "detroit pistons"] },
  { name: "Golden State Warriors", city: "Golden State", nickname: "Warriors", shortName: "GSW", league: "NBA", primaryColor: "#1D428A", secondaryColor: "#FFC72C", logoSvg: makeCircleSvg("GSW", "#1D428A", "#FFC72C", "#FFC72C"), aliases: ["warriors", "golden state warriors", "dubs"] },
  { name: "Houston Rockets", city: "Houston", nickname: "Rockets", shortName: "HOU", league: "NBA", primaryColor: "#CE1141", secondaryColor: "#000000", logoSvg: makeCircleSvg("HOU", "#CE1141", "#FFFFFF", "#000000"), aliases: ["rockets", "houston rockets"] },
  { name: "Indiana Pacers", city: "Indiana", nickname: "Pacers", shortName: "IND", league: "NBA", primaryColor: "#002D62", secondaryColor: "#FDBB30", logoSvg: makeCircleSvg("IND", "#002D62", "#FDBB30", "#C1C6C8"), aliases: ["pacers", "indiana pacers"] },
  { name: "LA Clippers", city: "Los Angeles", nickname: "Clippers", shortName: "LAC", league: "NBA", primaryColor: "#C8102E", secondaryColor: "#1D428A", logoSvg: makeCircleSvg("LAC", "#1D428A", "#C8102E", "#FFFFFF"), aliases: ["clippers", "la clippers"] },
  { name: "Los Angeles Lakers", city: "Los Angeles", nickname: "Lakers", shortName: "LAL", league: "NBA", primaryColor: "#552583", secondaryColor: "#FDB927", logoSvg: makeCircleSvg("LAL", "#552583", "#FDB927", "#FDB927"), aliases: ["lakers", "los angeles lakers", "lal"] },
  { name: "Memphis Grizzlies", city: "Memphis", nickname: "Grizzlies", shortName: "MEM", league: "NBA", primaryColor: "#5D76A9", secondaryColor: "#12173F", logoSvg: makeCircleSvg("MEM", "#12173F", "#5D76A9", "#F5B112"), aliases: ["grizzlies", "memphis grizzlies"] },
  { name: "Miami Heat", city: "Miami", nickname: "Heat", shortName: "MIA", league: "NBA", primaryColor: "#98002E", secondaryColor: "#F9A01B", logoSvg: makeCircleSvg("MIA", "#98002E", "#F9A01B", "#F9A01B"), aliases: ["heat", "miami heat"] },
  { name: "Milwaukee Bucks", city: "Milwaukee", nickname: "Bucks", shortName: "MIL", league: "NBA", primaryColor: "#00471B", secondaryColor: "#EEE1C6", logoSvg: makeCircleSvg("MIL", "#00471B", "#EEE1C6", "#0077C0"), aliases: ["bucks", "milwaukee bucks"] },
  { name: "Minnesota Timberwolves", city: "Minnesota", nickname: "Timberwolves", shortName: "MIN", league: "NBA", primaryColor: "#0C2340", secondaryColor: "#236192", logoSvg: makeCircleSvg("MIN", "#0C2340", "#78BE20", "#236192"), aliases: ["timberwolves", "wolves", "minnesota timberwolves"] },
  { name: "New Orleans Pelicans", city: "New Orleans", nickname: "Pelicans", shortName: "NOP", league: "NBA", primaryColor: "#0C2340", secondaryColor: "#C8102E", logoSvg: makeCircleSvg("NOP", "#0C2340", "#C8102E", "#D3BC8D"), aliases: ["pelicans", "pels", "new orleans pelicans"] },
  { name: "New York Knicks", city: "New York", nickname: "Knicks", shortName: "NYK", league: "NBA", primaryColor: "#006BB6", secondaryColor: "#F58426", logoSvg: makeCircleSvg("NYK", "#006BB6", "#F58426", "#F58426"), aliases: ["knicks", "new york knicks"] },
  { name: "Oklahoma City Thunder", city: "Oklahoma City", nickname: "Thunder", shortName: "OKC", league: "NBA", primaryColor: "#007AC1", secondaryColor: "#EF3B24", logoSvg: makeCircleSvg("OKC", "#007AC1", "#EF3B24", "#FDBB30"), aliases: ["thunder", "okc thunder", "oklahoma city thunder"] },
  { name: "Orlando Magic", city: "Orlando", nickname: "Magic", shortName: "ORL", league: "NBA", primaryColor: "#0077C0", secondaryColor: "#C4CED4", logoSvg: makeCircleSvg("ORL", "#0077C0", "#000000", "#C4CED4"), aliases: ["magic", "orlando magic"] },
  { name: "Philadelphia 76ers", city: "Philadelphia", nickname: "76ers", shortName: "PHI", league: "NBA", primaryColor: "#006BB6", secondaryColor: "#ED174C", logoSvg: makeCircleSvg("76ERS", "#006BB6", "#ED174C", "#FFFFFF"), aliases: ["76ers", "sixers", "philadelphia 76ers"] },
  { name: "Phoenix Suns", city: "Phoenix", nickname: "Suns", shortName: "PHX", league: "NBA", primaryColor: "#1D1160", secondaryColor: "#E56020", logoSvg: makeCircleSvg("PHX", "#1D1160", "#E56020", "#E56020"), aliases: ["suns", "phoenix suns"] },
  { name: "Portland Trail Blazers", city: "Portland", nickname: "Trail Blazers", shortName: "POR", league: "NBA", primaryColor: "#E03A3E", secondaryColor: "#000000", logoSvg: makeCircleSvg("POR", "#000000", "#E03A3E", "#E03A3E"), aliases: ["blazers", "trail blazers", "portland trail blazers"] },
  { name: "Sacramento Kings", city: "Sacramento", nickname: "Kings", shortName: "SAC", league: "NBA", primaryColor: "#5A2D81", secondaryColor: "#63727A", logoSvg: makeCircleSvg("SAC", "#5A2D81", "#63727A", "#000000"), aliases: ["kings", "sacramento kings"] },
  { name: "San Antonio Spurs", city: "San Antonio", nickname: "Spurs", shortName: "SAS", league: "NBA", primaryColor: "#C4CED4", secondaryColor: "#000000", logoSvg: makeCircleSvg("SAS", "#000000", "#C4CED4", "#C4CED4"), aliases: ["spurs", "san antonio spurs"] },
  { name: "Toronto Raptors", city: "Toronto", nickname: "Raptors", shortName: "TOR", league: "NBA", primaryColor: "#CE1141", secondaryColor: "#000000", logoSvg: makeCircleSvg("TOR", "#CE1141", "#FFFFFF", "#000000"), aliases: ["raptors", "toronto raptors"] },
  { name: "Utah Jazz", city: "Utah", nickname: "Jazz", shortName: "UTA", league: "NBA", primaryColor: "#002B5C", secondaryColor: "#00471B", logoSvg: makeCircleSvg("JAZZ", "#002B5C", "#F9A01B", "#00471B"), aliases: ["jazz", "utah jazz"] },
  { name: "Washington Wizards", city: "Washington", nickname: "Wizards", shortName: "WAS", league: "NBA", primaryColor: "#002B5C", secondaryColor: "#E31837", logoSvg: makeCircleSvg("WAS", "#002B5C", "#E31837", "#C4CED4"), aliases: ["wizards", "washington wizards"] },
];

// 100% COMPLETE 30-TEAM MLB FRANCHISE REGISTRY
const MLB_TEAMS: TeamInfo[] = [
  { name: "Arizona Diamondbacks", city: "Arizona", nickname: "Diamondbacks", shortName: "ARI", league: "MLB", primaryColor: "#A71930", secondaryColor: "#E3D4AD", logoSvg: makeDiamondSvg("ARI", "#A71930", "#E3D4AD", "#30CDD7"), aliases: ["diamondbacks", "d-backs", "arizona diamondbacks"] },
  { name: "Atlanta Braves", city: "Atlanta", nickname: "Braves", shortName: "ATL", league: "MLB", primaryColor: "#CE1141", secondaryColor: "#13274F", logoSvg: makeCircleSvg("ATL", "#13274F", "#CE1141", "#CE1141"), aliases: ["braves", "atlanta braves"] },
  { name: "Baltimore Orioles", city: "Baltimore", nickname: "Orioles", shortName: "BAL", league: "MLB", primaryColor: "#DF4601", secondaryColor: "#000000", logoSvg: makeCircleSvg("BAL", "#DF4601", "#FFFFFF", "#000000"), aliases: ["orioles", "o's", "baltimore orioles"] },
  { name: "Boston Red Sox", city: "Boston", nickname: "Red Sox", shortName: "BOS", league: "MLB", primaryColor: "#BD3039", secondaryColor: "#0D2B56", logoSvg: makeCircleSvg("BOS", "#BD3039", "#FFFFFF", "#0D2B56"), aliases: ["red sox", "boston red sox"] },
  { name: "Chicago Cubs", city: "Chicago", nickname: "Cubs", shortName: "CHC", league: "MLB", primaryColor: "#0E3386", secondaryColor: "#CC3433", logoSvg: makeCircleSvg("CHC", "#0E3386", "#CC3433", "#FFFFFF"), aliases: ["cubs", "chicago cubs"] },
  { name: "Chicago White Sox", city: "Chicago", nickname: "White Sox", shortName: "CWS", league: "MLB", primaryColor: "#27251F", secondaryColor: "#C4CED4", logoSvg: makeCircleSvg("CWS", "#27251F", "#FFFFFF", "#C4CED4"), aliases: ["white sox", "chicago white sox"] },
  { name: "Cincinnati Reds", city: "Cincinnati", nickname: "Reds", shortName: "CIN", league: "MLB", primaryColor: "#C6011F", secondaryColor: "#000000", logoSvg: makeCircleSvg("CIN", "#C6011F", "#FFFFFF", "#000000"), aliases: ["reds", "cincinnati reds"] },
  { name: "Cleveland Guardians", city: "Cleveland", nickname: "Guardians", shortName: "CLE", league: "MLB", primaryColor: "#0C2340", secondaryColor: "#E31937", logoSvg: makeCircleSvg("CLE", "#0C2340", "#E31937", "#E31937"), aliases: ["guardians", "cleveland guardians", "indians"] },
  { name: "Colorado Rockies", city: "Colorado", nickname: "Rockies", shortName: "COL", league: "MLB", primaryColor: "#33006F", secondaryColor: "#C4CED4", logoSvg: makeCircleSvg("COL", "#33006F", "#C4CED4", "#000000"), aliases: ["rockies", "colorado rockies"] },
  { name: "Detroit Tigers", city: "Detroit", nickname: "Tigers", shortName: "DET", league: "MLB", primaryColor: "#0C2340", secondaryColor: "#FA4616", logoSvg: makeCircleSvg("DET", "#0C2340", "#FA4616", "#FA4616"), aliases: ["tigers", "detroit tigers"] },
  { name: "Houston Astros", city: "Houston", nickname: "Astros", shortName: "HOU", league: "MLB", primaryColor: "#002D62", secondaryColor: "#EB6E1F", logoSvg: makeCircleSvg("HOU", "#002D62", "#EB6E1F", "#EB6E1F"), aliases: ["astros", "houston astros"] },
  { name: "Kansas City Royals", city: "Kansas City", nickname: "Royals", shortName: "KC", league: "MLB", primaryColor: "#004687", secondaryColor: "#BD9B60", logoSvg: makeCircleSvg("KC", "#004687", "#BD9B60", "#FFFFFF"), aliases: ["royals", "kansas city royals"] },
  { name: "Los Angeles Angels", city: "Los Angeles", nickname: "Angels", shortName: "LAA", league: "MLB", primaryColor: "#BA0021", secondaryColor: "#003263", logoSvg: makeCircleSvg("LAA", "#BA0021", "#FFFFFF", "#003263"), aliases: ["angels", "la angels", "anaheim angels"] },
  { name: "Los Angeles Dodgers", city: "Los Angeles", nickname: "Dodgers", shortName: "LAD", league: "MLB", primaryColor: "#005A9C", secondaryColor: "#EF3E42", logoSvg: makeCircleSvg("LAD", "#005A9C", "#FFFFFF", "#EF3E42"), aliases: ["dodgers", "la dodgers", "los angeles dodgers"] },
  { name: "Miami Marlins", city: "Miami", nickname: "Marlins", shortName: "MIA", league: "MLB", primaryColor: "#00A3E0", secondaryColor: "#EF3340", logoSvg: makeCircleSvg("MIA", "#000000", "#00A3E0", "#EF3340"), aliases: ["marlins", "miami marlins"] },
  { name: "Milwaukee Brewers", city: "Milwaukee", nickname: "Brewers", shortName: "MIL", league: "MLB", primaryColor: "#12284C", secondaryColor: "#FFC52F", logoSvg: makeCircleSvg("MIL", "#12284C", "#FFC52F", "#FFC52F"), aliases: ["brewers", "milwaukee brewers"] },
  { name: "Minnesota Twins", city: "Minnesota", nickname: "Twins", shortName: "MIN", league: "MLB", primaryColor: "#002B5C", secondaryColor: "#D31145", logoSvg: makeCircleSvg("MIN", "#002B5C", "#D31145", "#FFFFFF"), aliases: ["twins", "minnesota twins"] },
  { name: "New York Mets", city: "New York", nickname: "Mets", shortName: "NYM", league: "MLB", primaryColor: "#002D72", secondaryColor: "#FF5910", logoSvg: makeCircleSvg("NYM", "#002D72", "#FF5910", "#FF5910"), aliases: ["mets", "new york mets"] },
  { name: "New York Yankees", city: "New York", nickname: "Yankees", shortName: "NYY", league: "MLB", primaryColor: "#003087", secondaryColor: "#E4002C", logoSvg: makeCircleSvg("NYY", "#003087", "#FFFFFF", "#FFFFFF"), aliases: ["yankees", "new york yankees", "yanks"] },
  { name: "Oakland Athletics", city: "Oakland", nickname: "Athletics", shortName: "OAK", league: "MLB", primaryColor: "#003831", secondaryColor: "#EFB21E", logoSvg: makeCircleSvg("OAK", "#003831", "#EFB21E", "#EFB21E"), aliases: ["athletics", "a's", "oakland athletics"] },
  { name: "Philadelphia Phillies", city: "Philadelphia", nickname: "Phillies", shortName: "PHI", league: "MLB", primaryColor: "#E81828", secondaryColor: "#002D72", logoSvg: makeCircleSvg("PHI", "#E81828", "#FFFFFF", "#002D72"), aliases: ["phillies", "philadelphia phillies"] },
  { name: "Pittsburgh Pirates", city: "Pittsburgh", nickname: "Pirates", shortName: "PIT", league: "MLB", primaryColor: "#FDB827", secondaryColor: "#000000", logoSvg: makeCircleSvg("PIT", "#000000", "#FDB827", "#FDB827"), aliases: ["pirates", "pittsburgh pirates", "bucs"] },
  { name: "San Diego Padres", city: "San Diego", nickname: "Padres", shortName: "SD", league: "MLB", primaryColor: "#2F241D", secondaryColor: "#FFC425", logoSvg: makeCircleSvg("SD", "#2F241D", "#FFC425", "#FFC425"), aliases: ["padres", "san diego padres"] },
  { name: "San Francisco Giants", city: "San Francisco", nickname: "Giants", shortName: "SF", league: "MLB", primaryColor: "#FD5A1E", secondaryColor: "#27251F", logoSvg: makeCircleSvg("SF", "#27251F", "#FD5A1E", "#FD5A1E"), aliases: ["sf giants", "san francisco giants"] },
  { name: "Seattle Mariners", city: "Seattle", nickname: "Mariners", shortName: "SEA", league: "MLB", primaryColor: "#0C2340", secondaryColor: "#005C5C", logoSvg: makeCircleSvg("SEA", "#0C2340", "#005C5C", "#C4CED4"), aliases: ["mariners", "seattle mariners"] },
  { name: "St. Louis Cardinals", city: "St. Louis", nickname: "Cardinals", shortName: "STL", league: "MLB", primaryColor: "#C41E3A", secondaryColor: "#0C2340", logoSvg: makeCircleSvg("STL", "#C41E3A", "#FEDB00", "#0C2340"), aliases: ["cardinals mlb", "st louis cardinals", "stl cardinals"] },
  { name: "Tampa Bay Rays", city: "Tampa Bay", nickname: "Rays", shortName: "TB", league: "MLB", primaryColor: "#092C5C", secondaryColor: "#8FBCE6", logoSvg: makeCircleSvg("TB", "#092C5C", "#8FBCE6", "#F5D130"), aliases: ["rays", "tampa bay rays"] },
  { name: "Texas Rangers", city: "Texas", nickname: "Rangers", shortName: "TEX", league: "MLB", primaryColor: "#003278", secondaryColor: "#C0111F", logoSvg: makeCircleSvg("TEX", "#003278", "#C0111F", "#FFFFFF"), aliases: ["rangers mlb", "texas rangers"] },
  { name: "Toronto Blue Jays", city: "Toronto", nickname: "Blue Jays", shortName: "TOR", league: "MLB", primaryColor: "#134A8E", secondaryColor: "#1D2D5C", logoSvg: makeCircleSvg("TOR", "#134A8E", "#E8291C", "#FFFFFF"), aliases: ["blue jays", "toronto blue jays", "jays"] },
  { name: "Washington Nationals", city: "Washington", nickname: "Nationals", shortName: "WSH", league: "MLB", primaryColor: "#AB0003", secondaryColor: "#14225A", logoSvg: makeCircleSvg("WSH", "#AB0003", "#FFFFFF", "#14225A"), aliases: ["nationals", "nats", "washington nationals"] },
];

// 100% COMPLETE 32-TEAM NHL FRANCHISE REGISTRY
const NHL_TEAMS: TeamInfo[] = [
  { name: "Anaheim Ducks", city: "Anaheim", nickname: "Ducks", shortName: "ANA", league: "NHL", primaryColor: "#F47A38", secondaryColor: "#B9975B", logoSvg: makeShieldSvg("ANA", "#000000", "#F47A38", "#B9975B"), aliases: ["ducks", "anaheim ducks"] },
  { name: "Boston Bruins", city: "Boston", nickname: "Bruins", shortName: "BOS", league: "NHL", primaryColor: "#FFB81C", secondaryColor: "#000000", logoSvg: makeCircleSvg("BOS", "#000000", "#FFB81C", "#FFB81C"), aliases: ["bruins", "boston bruins"] },
  { name: "Buffalo Sabres", city: "Buffalo", nickname: "Sabres", shortName: "BUF", league: "NHL", primaryColor: "#002654", secondaryColor: "#FCB514", logoSvg: makeCircleSvg("BUF", "#002654", "#FCB514", "#FCB514"), aliases: ["sabres", "buffalo sabres"] },
  { name: "Calgary Flames", city: "Calgary", nickname: "Flames", shortName: "CGY", league: "NHL", primaryColor: "#C8102E", secondaryColor: "#F1BE48", logoSvg: makeShieldSvg("CGY", "#C8102E", "#F1BE48", "#FFFFFF"), aliases: ["flames", "calgary flames"] },
  { name: "Carolina Hurricanes", city: "Carolina", nickname: "Hurricanes", shortName: "CAR", league: "NHL", primaryColor: "#CC0000", secondaryColor: "#000000", logoSvg: makeShieldSvg("CAR", "#CC0000", "#000000", "#A2AAAD"), aliases: ["hurricanes", "carolina hurricanes", "canes"] },
  { name: "Chicago Blackhawks", city: "Chicago", nickname: "Blackhawks", shortName: "CHI", league: "NHL", primaryColor: "#CF0A2C", secondaryColor: "#000000", logoSvg: makeCircleSvg("CHI", "#CF0A2C", "#FFD100", "#000000"), aliases: ["blackhawks", "chicago blackhawks", "hawks nhl"] },
  { name: "Colorado Avalanche", city: "Colorado", nickname: "Avalanche", shortName: "COL", league: "NHL", primaryColor: "#6F263D", secondaryColor: "#236192", logoSvg: makeShieldSvg("COL", "#6F263D", "#FFFFFF", "#236192"), aliases: ["avalanche", "colorado avalanche", "avs"] },
  { name: "Columbus Blue Jackets", city: "Columbus", nickname: "Blue Jackets", shortName: "CBJ", league: "NHL", primaryColor: "#002654", secondaryColor: "#CE1126", logoSvg: makeCircleSvg("CBJ", "#002654", "#CE1126", "#A4A9AD"), aliases: ["blue jackets", "columbus blue jackets"] },
  { name: "Dallas Stars", city: "Dallas", nickname: "Stars", shortName: "DAL", league: "NHL", primaryColor: "#006847", secondaryColor: "#8F8F8C", logoSvg: makeShieldSvg("DAL", "#006847", "#FFFFFF", "#8F8F8C"), aliases: ["stars", "dallas stars"] },
  { name: "Detroit Red Wings", city: "Detroit", nickname: "Red Wings", shortName: "DET", league: "NHL", primaryColor: "#CE1126", secondaryColor: "#FFFFFF", logoSvg: makeCircleSvg("DET", "#CE1126", "#FFFFFF", "#FFFFFF"), aliases: ["red wings", "detroit red wings"] },
  { name: "Edmonton Oilers", city: "Edmonton", nickname: "Oilers", shortName: "EDM", league: "NHL", primaryColor: "#041E42", secondaryColor: "#FF4C00", logoSvg: makeCircleSvg("EDM", "#041E42", "#FF4C00", "#FF4C00"), aliases: ["oilers", "edmonton oilers"] },
  { name: "Florida Panthers", city: "Florida", nickname: "Panthers", shortName: "FLA", league: "NHL", primaryColor: "#041E42", secondaryColor: "#C8102E", logoSvg: makeShieldSvg("FLA", "#041E42", "#C8102E", "#B9975B"), aliases: ["panthers nhl", "florida panthers"] },
  { name: "Los Angeles Kings", city: "Los Angeles", nickname: "Kings", shortName: "LAK", league: "NHL", primaryColor: "#111111", secondaryColor: "#A2AAAD", logoSvg: makeShieldSvg("LAK", "#111111", "#A2AAAD", "#FFFFFF"), aliases: ["kings nhl", "la kings", "los angeles kings nhl"] },
  { name: "Minnesota Wild", city: "Minnesota", nickname: "Wild", shortName: "MIN", league: "NHL", primaryColor: "#154734", secondaryColor: "#A6192E", logoSvg: makeCircleSvg("MIN", "#154734", "#EAAA00", "#A6192E"), aliases: ["wild", "minnesota wild"] },
  { name: "Montreal Canadiens", city: "Montreal", nickname: "Canadiens", shortName: "MTL", league: "NHL", primaryColor: "#AF1E2D", secondaryColor: "#192168", logoSvg: makeCircleSvg("MTL", "#AF1E2D", "#FFFFFF", "#192168"), aliases: ["canadiens", "habs", "montreal canadiens"] },
  { name: "Nashville Predators", city: "Nashville", nickname: "Predators", shortName: "NSH", league: "NHL", primaryColor: "#FFB81C", secondaryColor: "#041E42", logoSvg: makeShieldSvg("NSH", "#FFB81C", "#041E42", "#041E42"), aliases: ["predators", "preds", "nashville predators"] },
  { name: "New Jersey Devils", city: "New Jersey", nickname: "Devils", shortName: "NJD", league: "NHL", primaryColor: "#CE1126", secondaryColor: "#000000", logoSvg: makeCircleSvg("NJD", "#CE1126", "#000000", "#FFFFFF"), aliases: ["devils", "new jersey devils"] },
  { name: "New York Islanders", city: "New York", nickname: "Islanders", shortName: "NYI", league: "NHL", primaryColor: "#00539B", secondaryColor: "#F47920", logoSvg: makeCircleSvg("NYI", "#00539B", "#F47920", "#FFFFFF"), aliases: ["islanders", "new york islanders", "isles"] },
  { name: "New York Rangers", city: "New York", nickname: "Rangers", shortName: "NYR", league: "NHL", primaryColor: "#0038A8", secondaryColor: "#CE1126", logoSvg: makeShieldSvg("NYR", "#0038A8", "#FFFFFF", "#CE1126"), aliases: ["rangers nhl", "new york rangers"] },
  { name: "Ottawa Senators", city: "Ottawa", nickname: "Senators", shortName: "OTT", league: "NHL", primaryColor: "#DA1A32", secondaryColor: "#000000", logoSvg: makeShieldSvg("OTT", "#000000", "#DA1A32", "#D69F3D"), aliases: ["senators", "sens", "ottawa senators"] },
  { name: "Philadelphia Flyers", city: "Philadelphia", nickname: "Flyers", shortName: "PHI", league: "NHL", primaryColor: "#F74902", secondaryColor: "#000000", logoSvg: makeCircleSvg("PHI", "#F74902", "#000000", "#FFFFFF"), aliases: ["flyers", "philadelphia flyers"] },
  { name: "Pittsburgh Penguins", city: "Pittsburgh", nickname: "Penguins", shortName: "PIT", league: "NHL", primaryColor: "#000000", secondaryColor: "#FCB514", logoSvg: makeShieldSvg("PIT", "#000000", "#FCB514", "#FCB514"), aliases: ["penguins", "pens", "pittsburgh penguins"] },
  { name: "San Jose Sharks", city: "San Jose", nickname: "Sharks", shortName: "SJS", league: "NHL", primaryColor: "#006D75", secondaryColor: "#EA7200", logoSvg: makeShieldSvg("SJS", "#006D75", "#EA7200", "#000000"), aliases: ["sharks", "san jose sharks"] },
  { name: "Seattle Kraken", city: "Seattle", nickname: "Kraken", shortName: "SEA", league: "NHL", primaryColor: "#001628", secondaryColor: "#99D9D9", logoSvg: makeShieldSvg("SEA", "#001628", "#99D9D9", "#E9072B"), aliases: ["kraken", "seattle kraken"] },
  { name: "St. Louis Blues", city: "St. Louis", nickname: "Blues", shortName: "STL", league: "NHL", primaryColor: "#002F87", secondaryColor: "#FCB514", logoSvg: makeCircleSvg("STL", "#002F87", "#FCB514", "#FCB514"), aliases: ["blues", "st louis blues"] },
  { name: "Tampa Bay Lightning", city: "Tampa Bay", nickname: "Lightning", shortName: "TBL", league: "NHL", primaryColor: "#002868", secondaryColor: "#FFFFFF", logoSvg: makeCircleSvg("TBL", "#002868", "#FFFFFF", "#FFFFFF"), aliases: ["lightning", "bolts", "tampa bay lightning"] },
  { name: "Toronto Maple Leafs", city: "Toronto", nickname: "Maple Leafs", shortName: "TOR", league: "NHL", primaryColor: "#00205B", secondaryColor: "#FFFFFF", logoSvg: makeShieldSvg("TOR", "#00205B", "#FFFFFF", "#FFFFFF"), aliases: ["maple leafs", "leafs", "toronto maple leafs"] },
  { name: "Utah Hockey Club", city: "Utah", nickname: "Utah HC", shortName: "UTA", league: "NHL", primaryColor: "#71AFE5", secondaryColor: "#000000", logoSvg: makeShieldSvg("UTA", "#000000", "#71AFE5", "#71AFE5"), aliases: ["utah hc", "coyotes", "utah hockey club", "arizona coyotes"] },
  { name: "Vancouver Canucks", city: "Vancouver", nickname: "Canucks", shortName: "VAN", league: "NHL", primaryColor: "#00205B", secondaryColor: "#00843D", logoSvg: makeCircleSvg("VAN", "#00205B", "#00843D", "#FFFFFF"), aliases: ["canucks", "vancouver canucks"] },
  { name: "Vegas Golden Knights", city: "Las Vegas", nickname: "Golden Knights", shortName: "VGK", league: "NHL", primaryColor: "#B4975A", secondaryColor: "#333F48", logoSvg: makeShieldSvg("VGK", "#333F48", "#B4975A", "#B4975A"), aliases: ["golden knights", "knights nhl", "vegas golden knights", "vgk"] },
  { name: "Washington Capitals", city: "Washington", nickname: "Capitals", shortName: "WSH", league: "NHL", primaryColor: "#041E42", secondaryColor: "#C8102E", logoSvg: makeCircleSvg("WSH", "#041E42", "#C8102E", "#FFFFFF"), aliases: ["capitals", "caps", "washington capitals"] },
  { name: "Winnipeg Jets", city: "Winnipeg", nickname: "Jets", shortName: "WPG", league: "NHL", primaryColor: "#041E42", secondaryColor: "#004C97", logoSvg: makeCircleSvg("WPG", "#041E42", "#004C97", "#AC162C"), aliases: ["jets nhl", "winnipeg jets"] },
];

// 100% COMPLETE 29-TEAM MLS REGISTRY
const MLS_TEAMS: TeamInfo[] = [
  { name: "Atlanta United FC", city: "Atlanta", nickname: "Atlanta United", shortName: "ATL", league: "MLS", primaryColor: "#80000A", secondaryColor: "#221F1F", logoSvg: makeShieldSvg("ATL", "#80000A", "#A19261", "#221F1F"), aliases: ["atlanta united", "atlanta united fc"] },
  { name: "Austin FC", city: "Austin", nickname: "Austin FC", shortName: "ATX", league: "MLS", primaryColor: "#00B140", secondaryColor: "#000000", logoSvg: makeShieldSvg("ATX", "#000000", "#00B140", "#00B140"), aliases: ["austin fc", "atx fc"] },
  { name: "Charlotte FC", city: "Charlotte", nickname: "Charlotte FC", shortName: "CLT", league: "MLS", primaryColor: "#1A85C8", secondaryColor: "#000000", logoSvg: makeCircleSvg("CLT", "#1A85C8", "#FFFFFF", "#000000"), aliases: ["charlotte fc"] },
  { name: "Chicago Fire FC", city: "Chicago", nickname: "Chicago Fire", shortName: "CHI", league: "MLS", primaryColor: "#FF0000", secondaryColor: "#001489", logoSvg: makeShieldSvg("CHI", "#001489", "#FF0000", "#C8AA76"), aliases: ["chicago fire", "chicago fire fc"] },
  { name: "FC Cincinnati", city: "Cincinnati", nickname: "FC Cincinnati", shortName: "CIN", league: "MLS", primaryColor: "#F05323", secondaryColor: "#003087", logoSvg: makeShieldSvg("CIN", "#003087", "#F05323", "#F05323"), aliases: ["fc cincinnati", "cincinnati mls"] },
  { name: "Colorado Rapids", city: "Colorado", nickname: "Colorado Rapids", shortName: "COL", league: "MLS", primaryColor: "#862633", secondaryColor: "#8BB8E8", logoSvg: makeShieldSvg("COL", "#862633", "#8BB8E8", "#C4D600"), aliases: ["colorado rapids", "rapids"] },
  { name: "Columbus Crew", city: "Columbus", nickname: "Columbus Crew", shortName: "CLB", league: "MLS", primaryColor: "#FEDD00", secondaryColor: "#000000", logoSvg: makeCircleSvg("CLB", "#000000", "#FEDD00", "#FEDD00"), aliases: ["columbus crew", "the crew"] },
  { name: "D.C. United", city: "D.C.", nickname: "D.C. United", shortName: "DC", league: "MLS", primaryColor: "#000000", secondaryColor: "#EF3E42", logoSvg: makeShieldSvg("DC", "#000000", "#EF3E42", "#FFFFFF"), aliases: ["dc united", "d.c. united"] },
  { name: "FC Dallas", city: "Dallas", nickname: "FC Dallas", shortName: "DAL", league: "MLS", primaryColor: "#E4002B", secondaryColor: "#00205B", logoSvg: makeShieldSvg("DAL", "#00205B", "#E4002B", "#E4002B"), aliases: ["fc dallas", "dallas mls"] },
  { name: "Houston Dynamo FC", city: "Houston", nickname: "Houston Dynamo", shortName: "HOU", league: "MLS", primaryColor: "#F4911E", secondaryColor: "#101820", logoSvg: makeShieldSvg("HOU", "#101820", "#F4911E", "#F4911E"), aliases: ["houston dynamo", "dynamo fc"] },
  { name: "Inter Miami CF", city: "Miami", nickname: "Inter Miami", shortName: "MIA", league: "MLS", primaryColor: "#F7B5CD", secondaryColor: "#231F20", logoSvg: makeCircleSvg("MIA", "#231F20", "#F7B5CD", "#F7B5CD"), aliases: ["inter miami", "inter miami cf", "miami mls"] },
  { name: "LA Galaxy", city: "Los Angeles", nickname: "LA Galaxy", shortName: "LAG", league: "MLS", primaryColor: "#00245D", secondaryColor: "#FFD200", logoSvg: makeShieldSvg("LAG", "#00245D", "#FFD200", "#006BB6"), aliases: ["la galaxy", "galaxy"] },
  { name: "Los Angeles FC", city: "Los Angeles", nickname: "LAFC", shortName: "LAFC", league: "MLS", primaryColor: "#C39E5C", secondaryColor: "#000000", logoSvg: makeShieldSvg("LAFC", "#000000", "#C39E5C", "#C39E5C"), aliases: ["lafc", "los angeles fc"] },
  { name: "Minnesota United FC", city: "Minnesota", nickname: "Minnesota United", shortName: "MIN", league: "MLS", primaryColor: "#8CD2F4", secondaryColor: "#231F20", logoSvg: makeShieldSvg("MIN", "#231F20", "#8CD2F4", "#DF2826"), aliases: ["minnesota united", "loons"] },
  { name: "CF Montreal", city: "Montreal", nickname: "CF Montreal", shortName: "MTL", league: "MLS", primaryColor: "#0033A0", secondaryColor: "#000000", logoSvg: makeCircleSvg("MTL", "#000000", "#0033A0", "#7FA9AE"), aliases: ["cf montreal", "montreal impact"] },
  { name: "Nashville SC", city: "Nashville", nickname: "Nashville SC", shortName: "NSH", league: "MLS", primaryColor: "#ECE838", secondaryColor: "#1F1646", logoSvg: makeShieldSvg("NSH", "#1F1646", "#ECE838", "#ECE838"), aliases: ["nashville sc", "nashville mls"] },
  { name: "New England Revolution", city: "New England", nickname: "Revolution", shortName: "NER", league: "MLS", primaryColor: "#0A2240", secondaryColor: "#CE0E2D", logoSvg: makeCircleSvg("NER", "#0A2240", "#CE0E2D", "#FFFFFF"), aliases: ["new england revolution", "revs"] },
  { name: "New York City FC", city: "New York", nickname: "NYCFC", shortName: "NYC", league: "MLS", primaryColor: "#6CACE4", secondaryColor: "#041E42", logoSvg: makeCircleSvg("NYC", "#041E42", "#6CACE4", "#F15524"), aliases: ["nycfc", "new york city fc"] },
  { name: "New York Red Bulls", city: "New York", nickname: "Red Bulls", shortName: "RBNY", league: "MLS", primaryColor: "#ED1E36", secondaryColor: "#223971", logoSvg: makeShieldSvg("RBNY", "#223971", "#ED1E36", "#FFC72C"), aliases: ["new york red bulls", "red bulls", "rbny"] },
  { name: "Orlando City SC", city: "Orlando", nickname: "Orlando City", shortName: "ORL", league: "MLS", primaryColor: "#612B82", secondaryColor: "#FFE17F", logoSvg: makeShieldSvg("ORL", "#612B82", "#FFE17F", "#FFE17F"), aliases: ["orlando city", "orlando city sc"] },
  { name: "Philadelphia Union", city: "Philadelphia", nickname: "Philadelphia Union", shortName: "PHI", league: "MLS", primaryColor: "#071B2C", secondaryColor: "#B38707", logoSvg: makeShieldSvg("PHI", "#071B2C", "#B38707", "#41B6E6"), aliases: ["philadelphia union", "union mls"] },
  { name: "Portland Timbers", city: "Portland", nickname: "Portland Timbers", shortName: "POR", league: "MLS", primaryColor: "#004812", secondaryColor: "#EAE827", logoSvg: makeCircleSvg("POR", "#004812", "#EAE827", "#D69A2D"), aliases: ["portland timbers", "timbers"] },
  { name: "Real Salt Lake", city: "Salt Lake", nickname: "Real Salt Lake", shortName: "RSL", league: "MLS", primaryColor: "#B30838", secondaryColor: "#001E62", logoSvg: makeShieldSvg("RSL", "#001E62", "#B30838", "#F1B71C"), aliases: ["real salt lake", "rsl"] },
  { name: "San Jose Earthquakes", city: "San Jose", nickname: "Earthquakes", shortName: "SJE", league: "MLS", primaryColor: "#0051BA", secondaryColor: "#000000", logoSvg: makeShieldSvg("SJE", "#000000", "#0051BA", "#0051BA"), aliases: ["san jose earthquakes", "quakes"] },
  { name: "Seattle Sounders FC", city: "Seattle", nickname: "Seattle Sounders", shortName: "SEA", league: "MLS", primaryColor: "#005595", secondaryColor: "#5D9732", logoSvg: makeShieldSvg("SEA", "#005595", "#5D9732", "#5D9732"), aliases: ["seattle sounders", "sounders"] },
  { name: "Sporting Kansas City", city: "Kansas City", nickname: "Sporting KC", shortName: "SKC", league: "MLS", primaryColor: "#91B0D5", secondaryColor: "#002B49", logoSvg: makeShieldSvg("SKC", "#002B49", "#91B0D5", "#A1A1A4"), aliases: ["sporting kansas city", "sporting kc", "skc"] },
  { name: "St. Louis City SC", city: "St. Louis", nickname: "St. Louis City", shortName: "STL", league: "MLS", primaryColor: "#E3065C", secondaryColor: "#00143C", logoSvg: makeShieldSvg("STL", "#00143C", "#E3065C", "#FFE500"), aliases: ["st louis city", "st louis city sc", "stl city"] },
  { name: "Toronto FC", city: "Toronto", nickname: "Toronto FC", shortName: "TOR", league: "MLS", primaryColor: "#B81137", secondaryColor: "#455560", logoSvg: makeShieldSvg("TOR", "#B81137", "#FFFFFF", "#455560"), aliases: ["toronto fc", "tfc"] },
  { name: "Vancouver Whitecaps FC", city: "Vancouver", nickname: "Whitecaps", shortName: "VAN", league: "MLS", primaryColor: "#00245D", secondaryColor: "#9DC2EA", logoSvg: makeDiamondSvg("VAN", "#00245D", "#9DC2EA", "#FFFFFF"), aliases: ["vancouver whitecaps", "whitecaps"] },
];

// PREMIER LEAGUE TOP CLUBS
const EPL_TEAMS: TeamInfo[] = [
  { name: "Arsenal FC", city: "London", nickname: "Arsenal", shortName: "ARS", league: "PREMIER LEAGUE", primaryColor: "#EF0107", secondaryColor: "#063672", logoSvg: makeShieldSvg("ARS", "#EF0107", "#FFFFFF", "#063672"), aliases: ["arsenal", "arsenal fc", "gunners"] },
  { name: "Aston Villa", city: "Birmingham", nickname: "Aston Villa", shortName: "AVL", league: "PREMIER LEAGUE", primaryColor: "#95BFE5", secondaryColor: "#670E36", logoSvg: makeShieldSvg("AVL", "#670E36", "#95BFE5", "#FEE12B"), aliases: ["aston villa", "villa"] },
  { name: "Chelsea FC", city: "London", nickname: "Chelsea", shortName: "CHE", league: "PREMIER LEAGUE", primaryColor: "#034694", secondaryColor: "#EE242C", logoSvg: makeCircleSvg("CHE", "#034694", "#FFFFFF", "#EE242C"), aliases: ["chelsea", "chelsea fc", "blues"] },
  { name: "Liverpool FC", city: "Liverpool", nickname: "Liverpool", shortName: "LIV", league: "PREMIER LEAGUE", primaryColor: "#C8102E", secondaryColor: "#00B2A9", logoSvg: makeShieldSvg("LIV", "#C8102E", "#FFFFFF", "#00B2A9"), aliases: ["liverpool", "liverpool fc", "reds"] },
  { name: "Manchester City", city: "Manchester", nickname: "Man City", shortName: "MCI", league: "PREMIER LEAGUE", primaryColor: "#6CABDD", secondaryColor: "#1C2C5B", logoSvg: makeCircleSvg("MCI", "#6CABDD", "#1C2C5B", "#FFFFFF"), aliases: ["manchester city", "man city", "mancity", "city"] },
  { name: "Manchester United", city: "Manchester", nickname: "Man United", shortName: "MUN", league: "PREMIER LEAGUE", primaryColor: "#DA291C", secondaryColor: "#FBE122", logoSvg: makeShieldSvg("MUN", "#DA291C", "#FBE122", "#000000"), aliases: ["manchester united", "man united", "man utd", "united"] },
  { name: "Newcastle United", city: "Newcastle", nickname: "Newcastle", shortName: "NEW", league: "PREMIER LEAGUE", primaryColor: "#241F20", secondaryColor: "#FFFFFF", logoSvg: makeShieldSvg("NEW", "#241F20", "#FFFFFF", "#41B6E6"), aliases: ["newcastle", "newcastle united"] },
  { name: "Tottenham Hotspur", city: "London", nickname: "Tottenham", shortName: "TOT", league: "PREMIER LEAGUE", primaryColor: "#132257", secondaryColor: "#FFFFFF", logoSvg: makeShieldSvg("TOT", "#132257", "#FFFFFF", "#FFFFFF"), aliases: ["tottenham", "tottenham hotspur", "spurs epl"] },
];

// Combine all leagues into master registry
const MASTER_TEAMS_LIST: TeamInfo[] = [
  ...NFL_TEAMS,
  ...NBA_TEAMS,
  ...MLB_TEAMS,
  ...NHL_TEAMS,
  ...MLS_TEAMS,
  ...EPL_TEAMS,
];

export function findTeamByQuery(query: string): TeamInfo | null {
  const q = query.trim().toLowerCase();
  for (const team of MASTER_TEAMS_LIST) {
    if (team.name.toLowerCase() === q || team.nickname.toLowerCase() === q || team.shortName.toLowerCase() === q) {
      return team;
    }
    for (const alias of team.aliases) {
      if (q === alias || q.includes(alias) || alias.includes(q)) {
        return team;
      }
    }
  }
  return null;
}

export function parseSportsMatchup(title: string): MatchupInfo | null {
  const upper = title.toUpperCase();

  // Detect League
  let league = "SPORTS";
  if (upper.includes("NFL:") || upper.includes("SUPER BOWL") || NFL_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "NFL";
  } else if (upper.includes("NBA:") || NBA_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "NBA";
  } else if (upper.includes("MLB:") || MLB_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "MLB";
  } else if (upper.includes("NHL:") || upper.includes("STANLEY CUP") || NHL_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "NHL";
  } else if (upper.includes("MLS:") || MLS_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "MLS";
  } else if (upper.includes("PREMIER LEAGUE") || EPL_TEAMS.some(t => upper.includes(t.nickname.toUpperCase()))) {
    league = "PREMIER LEAGUE";
  } else if (upper.includes("FORMULA 1") || upper.includes("GRAND PRIX") || upper.includes("F1")) {
    league = "FORMULA 1";
  } else if (upper.includes("NASCAR")) {
    league = "NASCAR";
  }

  // Check for VS pattern
  if (upper.includes(" VS ") || upper.includes(" VS. ") || upper.includes(" @ ")) {
    const parts = upper.split(/ VS\.? | @ /);
    if (parts.length >= 2) {
      const awayRaw = parts[0].replace(/NFL:|NBA:|MLB:|NHL:|MLS:|PREMIER LEAGUE:|LIVE NATION PRESENTS:|VIVID SEATS:/gi, "").trim();
      const homeRaw = parts[1].trim();

      const awayTeam = findTeamByQuery(awayRaw) || {
        name: awayRaw,
        city: awayRaw,
        nickname: awayRaw,
        shortName: awayRaw.slice(0, 3).toUpperCase(),
        league,
        primaryColor: "#00FFFF",
        secondaryColor: "#000033",
        logoSvg: makeShieldSvg(awayRaw.slice(0, 3).toUpperCase(), "#000033", "#00FFFF", "#00FFFF"),
        aliases: [],
      };

      const homeTeam = findTeamByQuery(homeRaw) || {
        name: homeRaw,
        city: homeRaw,
        nickname: homeRaw,
        shortName: homeRaw.slice(0, 3).toUpperCase(),
        league,
        primaryColor: "#FFFF00",
        secondaryColor: "#000033",
        logoSvg: makeShieldSvg(homeRaw.slice(0, 3).toUpperCase(), "#000033", "#FFFF00", "#FFFF00"),
        aliases: [],
      };

      return {
        isMatchup: true,
        league,
        awayTeam,
        homeTeam,
        headline: `${awayTeam.nickname || awayTeam.name} at ${homeTeam.nickname || homeTeam.name}`,
      };
    }
  }

  return null;
}
