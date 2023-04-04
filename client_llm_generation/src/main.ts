import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import DisplaySoftmax from './components/DisplaySoftmax.vue'
import DisplayConnections from './components/DisplayConnections.vue'

const routes = [
    { path: '/', component: DisplaySoftmax},
    { path: '/connections', component: DisplayConnections}
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})


import './assets/main.css'

const app = createApp(App)
app.use(router)
app.mount("#app")
