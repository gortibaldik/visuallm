<template>
  <nav v-if="display_router_view && componentInfos.length != 1">
    <router-link class="button" v-for="componentInfo in componentInfos" :to="componentInfo.path">{{ componentInfo.title }}
    </router-link>
  </nav>
  <main>
    <router-view v-if="display_router_view"></router-view>
    <div class="notLoaded" v-else>
      <h1>The routes from the backend haven't been loaded yet.</h1>
    </div>
  </main>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'
import { PollUntilSuccessGET } from './assets/pollUntilSuccessLib'
import MainContainer from './components/MainContainerComponent.vue'

/**
 * Information needed to create a new route and link in the navbar. It is
 * returned by BE.
 *
 * - title is the title that will appear in the navbar
 * - name is the unique name of the component
 * - path is the unique route
 * - default_fetch_path is the path from which the component will download
 *  information needed for its execution
 */
type ComponentInfo = {
  title: string
  name: string
  path: string
  default_fetch_path: string
}

export default defineComponent({
  data() {
    return {
      display_router_view: false,
      componentInfos: [] as ComponentInfo[],
      backendAddress: import.meta.env.VITE_API_URL as string,
      tryPoll: undefined as undefined | PollUntilSuccessGET
    }
  },
  watch: {
    // this is just a dummy route change toggler, when v-if=display_router_view
    // is set to false the component is deactivated (destroyed, unmounted), then
    // it is set to true, and the component is again loaded, this allows multiple
    // routes to reuse the same component
    $route(to: any, from: any) {
      this.display_router_view = false
    },
    display_router_view(newValue: boolean) {
      if (newValue === false) {
        this.display_router_view = true
      }
    }
  },
  components: {
    MainContainer
  },
  provide() {
    return {
      backendAddress: this.backendAddress
    }
  },
  async created() {
    if (this.display_router_view) {
      return
    }
    this.tryPoll = new PollUntilSuccessGET(
      `${this.backendAddress}/fetch_components`,
      this.resolveComponents.bind(this)
    )
    await this.tryPoll.newRequest()
  },
  unmounted() {
    this.tryPoll?.clear()
  },
  methods: {
    setDefaultPath(c: ComponentInfo) {
      c.path = '/'
      this.$router.removeRoute('default')
      return true
    },
    /** Register a tab component into router.
     * @param c
     */
    registerComponent(c: ComponentInfo) {
      let replace = false
      if (this.componentInfos.length == 0) {
        replace = this.setDefaultPath(c)
      } else {
        c.path = `/${c.name}`
      }
      this.componentInfos.push(c)
      this.$default_fetch_paths[c.name] = c.default_fetch_path
      if (replace) {
        this.$default_fetch_paths['default'] = c.default_fetch_path
      }
      this.$router.addRoute({
        name: c.name,
        path: c.path,
        component: MainContainer
      })
      return replace
    },
    isAlreadyRegistered(c: ComponentInfo) {
      return this.$router.hasRoute(c.name)
    },
    resolveComponents(response: any) {
      let context = response.context as ComponentInfo[]
      let replace = false
      for (let i = 0; i < context.length; i++) {
        let c = context[i]
        if (this.isAlreadyRegistered(c)) {
          continue
        }
        replace = this.registerComponent(c) || replace
      }
      if (replace) {
        this.$router.replace(this.$router.currentRoute.value.fullPath)
      }
      this.display_router_view = true
    }
  }
})
</script>

<style scoped>
nav {
  margin-bottom: 10px;
  background-color: rgb(192, 192, 192);
  margin-top: -2rem;
  margin-right: -2rem;
  margin-left: -2rem;
}

.notLoaded {
  text-align: center;
}

.router-link-active {
  color: black;
}
</style>
