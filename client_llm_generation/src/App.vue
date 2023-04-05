<template>
  <nav v-if="routes_already_loaded">
    <router-link class="button" v-for="route in customRoutes" :to="route.path">{{ route.title }} </router-link>
  </nav>
  <main>
    <router-view v-if="routes_already_loaded"></router-view>
    <div class="notLoaded" v-else>
      <h1>The routes from the backend haven't been loaded yet.</h1>
    </div>
  </main>
</template>

<script lang="ts" scoped>

import { defineComponent, shallowRef } from 'vue';
import type { Component } from 'vue';
import { PollUntilSuccessGET } from './assets/pollUntilSuccessLib'
import  NextTokenPrediction  from './components/NextTokenPrediction.vue'
import DisplayConnections from './components/DisplayConnections.vue'

type CustomRoute = {
  title: string;
  name: string;
  path: string;
}

export default defineComponent({
  data() {
    return {
      routes_already_loaded: false,
      customRoutes: [] as CustomRoute[],
      backendAddress: import.meta.env.VITE_API_URL as string,
      tryPoll: undefined as undefined | PollUntilSuccessGET,
      existingComponents: {
        "next_token_prediction": shallowRef(NextTokenPrediction),
        "connections": shallowRef(DisplayConnections),
      } as {[name: string] : Component}
    }
  },
  provide() {
    return {
      backendAddress: this.backendAddress
    }
  },
  created() {
    if (this.routes_already_loaded) {
      return
    }
    this.tryPoll = new PollUntilSuccessGET(
      `${this.backendAddress}/fetch_components`,
      this.resolveComponents.bind(this)
    )
    this.tryPoll.newRequest()
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
      this.$router.addRoute({
        name: c.name,
        path: c.path,
        component: this.existingComponents[c.name]
      })
      if (replace) {
        this.$router.replace(this.$router.currentRoute.value.fullPath)
      }

    },
    shouldBeRegistered(c : CustomRoute) {
      return c.name in this.existingComponents
    },
    isAlreadyRegistered(c: CustomRoute) {
      return this.$router.hasRoute(c.name)
    },
    resolveComponents(response: any) {
      let context = response.context as []
      for (let i = 0; i < context.length; i++) {
        let c = context[i] as CustomRoute
        if (this.shouldBeRegistered(c)) {
          if (this.isAlreadyRegistered(c)) {
            continue
          }
          this.registerComponent(c)
        }
      }
      this.routes_already_loaded = true

    }
  }
})

</script>

<style scoped>
nav {
  margin-bottom: 10px;
  background-color: rgb(192, 192, 192);
  padding: 20px;
  margin-top: -2rem;
  margin-right: -2rem;
  margin-left: -2rem;
}

.notLoaded {
  text-align: center;
}

.button {
  background-color: rgba(0, 0, 0, 0.409);
  padding: 20px;
  font-family: sans-serif;
  font-weight: normal;
  text-decoration: none;
  font-size: large;
  color: rgb(59, 59, 59);
  margin-right: 2px;
}

.button:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.router-link-active {
  color: black;
}
</style>