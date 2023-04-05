import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

const routes = [
    { name: 'default', path: '/', component: App},
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})


import './assets/main.css'

const app = createApp(App)
app.use(router)
app.mount("#app")
