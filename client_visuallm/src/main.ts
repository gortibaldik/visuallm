import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { registerElement as registerPlain } from './components/Element_PlainText.vue'
import { registerElement as registerBarChartSelect } from './components/Element_BarChartSelect.vue'
import { registerElement as registerTables } from './components/Element_Tables.vue'
import { registerElement as registerSampleSelector } from './components/Element_Selector.vue'
import ElementRegistry from './assets/elementRegistry'
import FetchPathsResolver from './assets/fetchPathsResolver'

const routes = [{ name: 'default', path: '/', component: App }]

const elementRegistry = new ElementRegistry()
registerPlain(elementRegistry)
registerBarChartSelect(elementRegistry)
registerTables(elementRegistry)
registerSampleSelector(elementRegistry)

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

import './assets/main.css'

const app = createApp(App)
app.use(elementRegistry)
app.use(router)
app.use(FetchPathsResolver)

declare module 'vue' {
  interface ComponentCustomProperties {
    $elementRegistry: ElementRegistry
    $default_fetch_paths: { [name: string]: string }
  }
}

app.mount('#app')
