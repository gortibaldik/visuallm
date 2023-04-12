<template>
  <nav v-if="display_router_view && (customRoutes.length != 1)">
    <router-link class="button" v-for="route in customRoutes" :to="route.path">{{ route.title }} </router-link>
  </nav>
  <main>
    <router-view v-if="display_router_view"></router-view>
    <div class="notLoaded" v-else>
      <h1>The routes from the backend haven't been loaded yet.</h1>
    </div>
  </main>
</template>

<script lang="ts" scoped>

import { defineComponent } from 'vue';
import { PollUntilSuccessGET } from './assets/pollUntilSuccessLib'
import  MainContainer  from './components/MainContainerComponent.vue'

type CustomRoute = {
  title: string;
  name: string;
  path: string;
  default_fetch_path: string;
}

export default defineComponent({
  data() {
    return {
      display_router_view: false,
      customRoutes: [] as CustomRoute[],
      backendAddress: import.meta.env.VITE_API_URL as string,
      tryPoll: undefined as undefined | PollUntilSuccessGET,
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
    MainContainer,
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
    setDefaultPath(c: CustomRoute) {
      c.path = "/"
      this.$router.removeRoute('default')
      return true
    },
    registerComponent(c: CustomRoute) {
      let replace = false
      if (this.customRoutes.length == 0) {
        replace = this.setDefaultPath(c)
      } else {
        c.path = `/${c.name}`
      }
      this.customRoutes.push(c)
      this.$default_fetch_paths[c.name] = c.default_fetch_path
      if (replace) {
        this.$default_fetch_paths["default"] = c.default_fetch_path
      }
      this.$router.addRoute({
        name: c.name,
        path: c.path,
        component: MainContainer,        
      })
      return replace
    },
    isAlreadyRegistered(c: CustomRoute) {
      return this.$router.hasRoute(c.name)
    },
    resolveComponents(response: any) {
      let context = response.context as []
      let replace = false;
      for (let i = 0; i < context.length; i++) {
        let c = context[i] as CustomRoute
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