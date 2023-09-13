<template>
  <nav v-if="display_router_view && componentInfos.length != 1" ref="nav_menu">
    <router-link class="nav-element" v-for="componentInfo in componentInfos" :key="componentInfo.path"
      :to="componentInfo.path">{{
        componentInfo.title }}
    </router-link>
  </nav>
  <main>
    <!-- component is loaded from the router-view, component is registered into the route -->
    <router-view v-if="display_router_view"></router-view>
    <div class="notLoaded" v-else>
      <h1>The routes from the backend haven't been loaded yet.</h1>
    </div>
  </main>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'
import { PollUntilSuccessGET } from './assets/pollUntilSuccessLib'
import MainContainer from './FrontendComponent.vue'

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
      /**
       * information about componentInfos
       */
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
    $route() {
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
      `${this.backendAddress}/fetch_component_infos`,
      this.registerComponentInfos.bind(this)
    )
    await this.tryPoll.newRequest()
  },
  unmounted() {
    this.tryPoll?.clear()
    window.removeEventListener("resize", this.resizeEventHandler);
  },
  mounted() {
    window.addEventListener("resize", this.resizeEventHandler);
  },
  methods: {
    /**
     * TODO: As of now, this is only a dummy method, in my plans I want to create a hamburger menu
     * or whole upper bar according to the lengths of upper bar. However this is on the end
     * of my priority list.
     */
    resizeEventHandler(e: any) {
    },
    /**
     * Reset component path to default option "/" and
     * remove "default" from the routes in router
     */
    setPathToDefault(c: ComponentInfo) {
      c.path = '/'
      this.$router.removeRoute('default')
    },
    /** Register a tab component into router. If a new default path is registered
     * returns true, otherwise false.
     */
    registerComponent(c: ComponentInfo) {
      let shouldReload = false
      // if there is no component yet registered, change the component path to
      // default path ('/')
      if (this.componentInfos.length == 0) {
        this.setPathToDefault(c)
        shouldReload = true
      } else {
        c.path = `/${c.name}`
      }
      this.componentInfos.push(c)
      this.$default_fetch_paths[c.name] = c.default_fetch_path
      if (shouldReload) {
        this.$default_fetch_paths['default'] = c.default_fetch_path
      }
      this.$router.addRoute({
        name: c.name,
        path: c.path,
        component: MainContainer
      })
      return shouldReload
    },
    isAlreadyRegistered(c: ComponentInfo) {
      return this.$router.hasRoute(c.name)
    },
    /** This method traverses the response from the backend and populates router
     * paths and optionaly reloads the whole page.
     */
    registerComponentInfos(response: any) {
      let componentInfos = response.component_infos as ComponentInfo[]
      let reloadCurrentPath = false
      for (let i = 0; i < componentInfos.length; i++) {
        let c = componentInfos[i]
        if (this.isAlreadyRegistered(c)) {
          continue
        }
        reloadCurrentPath = this.registerComponent(c) || reloadCurrentPath
      }
      if (reloadCurrentPath) {
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
  margin-top: -32px;
  margin-right: -2rem;
  margin-left: -2rem;
  display: flex;
  justify-content: flex-start;
  row-gap: 1px;
  column-gap: 1px;
}

.nav-element {
  background-color: rgba(0, 0, 0, 0.409);
  padding: 10px;
  padding-top: 5px;
  padding-bottom: 5px;
  font-family: sans-serif;
  font-weight: normal;
  text-decoration: none;
  font-size: large;
  color: rgb(76, 76, 76);
  height: fit-content;
}

.nav-element:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.notLoaded {
  text-align: center;
}

.router-link-active {
  color: black;
}
</style>
