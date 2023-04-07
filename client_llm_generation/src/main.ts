import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { registerComponent as registerPlain } from './components/DisplayPlainTextComponent.vue'
import { registerComponent as registerSoftmax } from './components/DisplaySoftmaxComponent.vue'
import { registerComponent as registerTables } from './components/DisplayLinksComponent.vue'
import Formatter from './assets/formatter'

const routes = [
    { name: 'default', path: '/', component: App},
]

const formatter = new Formatter()
registerPlain(formatter)
registerSoftmax(formatter)
registerTables(formatter)

const router = createRouter({
    history: createWebHashHistory(),
    routes
})


import './assets/main.css'

const app = createApp(App)
app.use(formatter)
app.use(router)

declare module 'vue' {
    interface ComponentCustomProperties {
        $formatter: Formatter
    }
}

app.mount("#app")