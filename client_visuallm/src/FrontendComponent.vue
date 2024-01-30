<template>
  <div class="horizontal rounded">
    <component v-for="(element, idx) in elements" :key="idx" :is="element.component" :name="element.name" v-on="shouldListenForReloadPage(element) ? {reloadPage} : {}"></component>
  </div>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'
import type { PollUntilSuccessGET } from '@/assets/pollUntilSuccessLib'
import type { ProcessedContext, ResponseFormat } from '@/assets/elementRegistry'
import PlainText from './elements/PlainText.vue'
import BarChartSelect from './elements/BarChartSelect.vue'
import Selector from './elements/Selector.vue'
import Tables from './elements/Tables.vue'
import Collapsible from './elements/Collapsible.vue'
import { fetchDefault } from '@/assets/fetchPathsResolver'
import { dataSharedInComponent } from '@/assets/reactiveData'

export default defineComponent({
  data() {
    return {
      elements: [] as ProcessedContext[],
      elementsWithReloadCapability: ['Selector', 'Collapsible'],
      defaultPoll: undefined as PollUntilSuccessGET | undefined
    }
  },
  inject: ['backendAddress'],
  async created() {
    /** TODO: Add some message during loading */
    await fetchDefault(
      this,
      this.backendAddress as string,
      'defaultPoll',
      this.setUpElements.bind(this)
    )
  },
  unmounted() {
    this.defaultPoll?.clear()
    this.resetComponentSharedData()
  },
  components: {
    PlainText,
    BarChartSelect,
    Selector,
    Tables,
    Collapsible
  },
  methods: {
    /**
     * remove all the remembered informations from the shared data store
     */
    resetComponentSharedData() {
      for (const key in dataSharedInComponent) {
        delete dataSharedInComponent[key]
      }
    },
    reloadPage(response: any) {
      this.setUpElements(response)
      this.$forceUpdate()
    },
    shouldListenForReloadPage(component: ProcessedContext) {
      return this.elementsWithReloadCapability.includes(component.component)
    },
    /**
     * extract all the elements from the response and populate the component
     * @param response
     */
    setUpElements(response: ResponseFormat) {
      this.elements = []
      this.$elementRegistry.retrieveElementsFromResponse(response, dataSharedInComponent, this.elements)
    },
  }
})
</script>
