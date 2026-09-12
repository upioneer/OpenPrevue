import { ref } from 'vue'

const STORAGE_KEY_DISMISS = 'openprevue_dismiss_onboarding_modal'
const STORAGE_KEY_COMPLETED = 'openprevue_onboarding_completed'

export const isOnboardingModalOpen = ref(false)

export function isDismissedOnStartup(): boolean {
  return (
    localStorage.getItem(STORAGE_KEY_DISMISS) === '1' ||
    localStorage.getItem(STORAGE_KEY_COMPLETED) === '1'
  )
}

export function setDismissOnStartup(dismiss: boolean): void {
  if (dismiss) {
    localStorage.setItem(STORAGE_KEY_DISMISS, '1')
    localStorage.setItem(STORAGE_KEY_COMPLETED, '1')
  } else {
    localStorage.removeItem(STORAGE_KEY_DISMISS)
    localStorage.removeItem(STORAGE_KEY_COMPLETED)
  }
}

export function openOnboardingModal(): void {
  isOnboardingModalOpen.value = true
}

export function closeOnboardingModal(neverShowAgain = false): void {
  // Always mark onboarding as completed on first launch once closed
  localStorage.setItem(STORAGE_KEY_COMPLETED, '1')
  if (neverShowAgain) {
    localStorage.setItem(STORAGE_KEY_DISMISS, '1')
  }
  isOnboardingModalOpen.value = false
}

export function resetOnboardingModalPreference(): void {
  localStorage.removeItem(STORAGE_KEY_DISMISS)
  localStorage.removeItem(STORAGE_KEY_COMPLETED)
}
