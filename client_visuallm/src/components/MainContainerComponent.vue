<script lang="ts" scoped>
import { defineComponent } from 'vue'
import type { PollUntilSuccessGET } from '@/assets/pollUntilSuccessLib'
import type { ProcessedContext, ElementDescription } from '@/assets/elementRegistry'
import Element_PlainText from './Element_PlainText.vue'
import Element_BarChartSelect from './Element_BarChartSelect.vue'
import Element_Selector from './Element_Selector.vue'
import Element_Tables from './Element_Tables.vue'
import Element_TextInput from './Element_TextInput.vue'
import { fetchDefault } from '@/assets/fetchPathsResolver'
import { componentSharedData } from '@/assets/reactiveData'

export default defineComponent({
  data() {
    return {
      elements: {} as { [name: string]: ProcessedContext },
      reactiveStore: componentSharedData,
      defaultPoll: undefined as PollUntilSuccessGET | undefined
    }
  },
  inject: ['backendAddress'],
  async created() {
    await this.fetchInitDataFromServer()
  },
  unmounted() {
    this.defaultPoll?.clear()
    this.resetReactiveStore()
  },
  components: {
    Element_PlainText,
    Element_BarChartSelect,
    Element_Selector,
    Element_Tables,
    Element_TextInput
  },
  methods: {
    resetReactiveStore() {
      for (const key in this.reactiveStore) {
        delete this.reactiveStore[key]
      }
    },
    setUpContext(response: { elementDescriptions: ElementDescription[] }) {
      this.$elementRegistry.retrieveElementsFromResponse(response, this.reactiveStore, this.elements)
    },
    async fetchInitDataFromServer() {
      await fetchDefault(
        this,
        this.backendAddress as string,
        'defaultPoll',
        this.setUpContext.bind(this)
      )
    }
  }
})
</script>

<template>
  <div class="horizontal rounded">
    <component v-for="(element, name) in elements" :is="element.component" :name="element.name"></component>
  </div>
</template>
