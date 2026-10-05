import { ref } from 'vue'
import type { EventItem } from '../types'

export const isEventModalOpen = ref(false)
export const selectedEvent = ref<EventItem | null>(null)

export function openEventModal(event: EventItem): void {
  selectedEvent.value = event
  isEventModalOpen.value = true
}

export function closeEventModal(): void {
  isEventModalOpen.value = false
  selectedEvent.value = null
}
