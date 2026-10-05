import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { retroShader } from './services/retroShader'

// Initialize vintage CRT shaders, scanlines, and color palette presets from localStorage
retroShader.init()

const app = createApp(App)
app.use(router)
app.mount('#app')

