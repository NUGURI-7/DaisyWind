import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Components from '@/components'

import App from './App.vue'
import router from './router'
import './app.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Components)

app.mount('#app')
