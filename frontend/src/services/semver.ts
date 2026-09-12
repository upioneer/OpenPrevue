/**
 * Semantic version parsing and strict comparison utilities.
 */

export function parseSemver(versionStr: string): [number, number, number] {
  if (!versionStr) return [0, 0, 0]
  const cleaned = versionStr.trim().replace(/^v/, '')
  const parts = cleaned.split('.')
  try {
    const major = parts.length > 0 ? parseInt(parts[0], 10) || 0 : 0
    const minor = parts.length > 1 ? parseInt(parts[1], 10) || 0 : 0
    const patch = parts.length > 2 ? parseInt(parts[2].split('-')[0], 10) || 0 : 0
    return [major, minor, patch]
  } catch {
    return [0, 0, 0]
  }
}

export function isNewerVersion(current: string, target: string): boolean {
  if (!current || !target) return false
  const [currMaj, currMin, currPat] = parseSemver(current)
  const [tgtMaj, tgtMin, tgtPat] = parseSemver(target)
  if (tgtMaj > currMaj) return true
  if (tgtMaj < currMaj) return false
  if (tgtMin > currMin) return true
  if (tgtMin < currMin) return false
  return tgtPat > currPat
}
