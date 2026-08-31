import { ref } from 'vue'

export const isSpotifyModalOpen = ref(false)

export function openSpotifyModal() {
  isSpotifyModalOpen.value = true
}

export function closeSpotifyModal() {
  isSpotifyModalOpen.value = false
}
