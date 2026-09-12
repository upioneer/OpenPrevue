import { ref } from 'vue'

const STORAGE_KEY_DISMISS = 'openprevue_dismiss_changelog_modal'
const STORAGE_KEY_LAST_SEEN = 'openprevue_last_seen_version'

export const isChangelogModalOpen = ref(false)
export const activeChangelogVersion = ref('0.24.0')

export function isChangelogDismissed(): boolean {
  return localStorage.getItem(STORAGE_KEY_DISMISS) === '1'
}

export function getLastSeenVersion(): string | null {
  return localStorage.getItem(STORAGE_KEY_LAST_SEEN)
}

export function setLastSeenVersion(version: string): void {
  localStorage.setItem(STORAGE_KEY_LAST_SEEN, version.replace(/^v/, ''))
}

export function setDismissChangelog(dismiss: boolean): void {
  if (dismiss) {
    localStorage.setItem(STORAGE_KEY_DISMISS, '1')
  } else {
    localStorage.removeItem(STORAGE_KEY_DISMISS)
  }
}

export function openChangelogModal(version?: string): void {
  if (version) {
    activeChangelogVersion.value = version.replace(/^v/, '')
  }
  isChangelogModalOpen.value = true
}

export function closeChangelogModal(neverShowAgain = false, currentVersion?: string): void {
  if (neverShowAgain) {
    setDismissChangelog(true)
  }
  if (currentVersion) {
    setLastSeenVersion(currentVersion)
  } else if (activeChangelogVersion.value) {
    setLastSeenVersion(activeChangelogVersion.value)
  }
  isChangelogModalOpen.value = false
}

export function checkShouldShowChangelog(currentVersion: string): boolean {
  if (isChangelogDismissed()) {
    return false
  }

  const cleanCurrent = currentVersion.replace(/^v/, '')
  const lastSeen = getLastSeenVersion()

  // First time client is run: record current version without popping modal immediately
  if (!lastSeen) {
    setLastSeenVersion(cleanCurrent)
    return false
  }

  // If installed version is newer or different from last seen version, trigger changelog modal
  if (lastSeen !== cleanCurrent) {
    activeChangelogVersion.value = cleanCurrent
    return true
  }

  return false
}

export function resetChangelogPreference(): void {
  setDismissChangelog(false)
  localStorage.removeItem(STORAGE_KEY_LAST_SEEN)
}
