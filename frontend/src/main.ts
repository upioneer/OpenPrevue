import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { retroShader } from './services/retroShader'
import { commercialsEngine } from './services/commercialsEngine'

// Initialize vintage CRT shaders, scanlines, and color palette presets from localStorage
retroShader.init()

// Expose services on window for diagnostics and automated verification
if (typeof window !== 'undefined') {
  ;(window as any).__commercialsEngine = commercialsEngine
}

const app = createApp(App)
app.use(router)
app.mount('#app')
