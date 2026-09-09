import { ref } from 'vue'

export const isUpdateModalOpen = ref(false)
export const updateModalTargetVersion = ref<string | null>(null)

export function openUpdateModal(targetVersion?: string) {
  updateModalTargetVersion.value = targetVersion || null
  isUpdateModalOpen.value = true
}

export function closeUpdateModal() {
  isUpdateModalOpen.value = false
}
