import { createApp } from 'vue'
import { createPinia } from 'pinia'
// Theme fonts (self-hosted): Plus Jakarta Sans for text, Fraunces for display headings
// (optical-size axis, so big headlines get the fine display cut). Devanagari falls back to Noto Sans.
import '@fontsource-variable/plus-jakarta-sans'
import '@fontsource-variable/fraunces/opsz.css'
import '@fontsource-variable/fraunces/opsz-italic.css'
import '@fontsource/noto-sans-devanagari/400.css'
import '@fontsource/noto-sans-devanagari/600.css'
import './styles/main.scss'

import App from './App.vue'
import router from './router'
import { i18n } from './i18n'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
document.documentElement.setAttribute('lang', i18n.global.locale.value)
app.mount('#app')
