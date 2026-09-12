import { ref } from 'vue'

export const isUpdateModalOpen = ref(false)
export const updateModalTargetVersion = ref<string | null>(null)
export const updateModalDiagnosticMode = ref(false)

export function openUpdateModal(targetVersion?: string, diagnosticMode = false) {
  updateModalTargetVersion.value = targetVersion || null
  updateModalDiagnosticMode.value = diagnosticMode
  isUpdateModalOpen.value = true
}

export function closeUpdateModal() {
  isUpdateModalOpen.value = false
  updateModalDiagnosticMode.value = false
}

