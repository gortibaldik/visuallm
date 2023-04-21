import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { registerComponent as registerPlain } from './components/DisplayPlainTextComponent.vue'
import { registerComponent as registerSoftmax } from './components/DisplaySoftmaxComponent.vue'
import { registerComponent as registerTables } from './components/DisplayLinksComponent.vue'
import { registerComponent as registerSampleSelector } from './components/DisplaySampleSelector.vue'
import Formatter from './assets/formatter'
import FetchPathsResolver from './assets/fetchPathsResolver'

const routes = [{ name: 'default', path: '/', component: App }]

const formatter = new Formatter()
registerPlain(formatter)
registerSoftmax(formatter)
registerTables(formatter)
registerSampleSelector(formatter)

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

import './assets/main.css'

const app = createApp(App)
app.use(formatter)
app.use(router)
app.use(FetchPathsResolver)

declare module 'vue' {
  interface ComponentCustomProperties {
    $formatter: Formatter
    $default_fetch_paths: { [name: string]: string }
  }
}

app.mount('#app')
