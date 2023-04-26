<template>
  <div class="wrapElement">
    <div v-for="barInfo in barInfos" class="progress-bar">
      <input v-if="selectable" class="input-radio" type="radio" v-model="picked" :value="barInfo.barTitle" />
      <DisplayPercentageComponent style="display: inline-block; width: 90%" :item="barInfo" :longContexts="longContexts"
        :names="names">
      </DisplayPercentageComponent>
    </div>
    <div v-if="selectable" style="text-align: center; margin-top: 10px">
      <button class="button" @click="emitClicked()">Select "{{ picked }}"</button>
    </div>
  </div>
</template>

<script lang="ts" scoped>
import { shallowRef } from 'vue'
import { defineComponent } from 'vue'
import { componentSharedData, getSharedDataUniqueName } from '@/assets/reactiveData'
import type Formatter from '@/assets/elementRegistry'
import type { ElementDescription } from '@/assets/elementRegistry'
import { configurationRequired, valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import DisplayPercentageComponent from './SubElement_BarCharSelect_Bar.vue'
import type { BarInfo } from './SubElement_BarCharSelect_Bar.vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  inject: ['backendAddress'],
  computed: {
    /** Title and bar heights of each row to be displayed
     */
    barInfos(): BarInfo[] {
      return componentSharedData[getSharedDataUniqueName(this.name, 'barInfos')]
    },
    /** Path to endpoint which is called when select button is pressed
     */
    address(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'address')]
    },
    /** Names of individual bar-charts to be displayed (e.g. each row can have
     * multiple bar-charts and each of them has a name)
     *
     */
    names(): string[] {
      return componentSharedData[getSharedDataUniqueName(this.name, 'names')]
    },
    longContexts(): boolean {
      return componentSharedData[getSharedDataUniqueName(this.name, 'longContexts')]
    },
    /** Bar chart could be either treated as a selection advice, e.g. add
     * input radio before each bar and select button at the end to help user
     * make informed selection, or it can be treated solely as an information
     * panel and then no select button or input radio should be added.
     */
    selectable(): boolean {
      return componentSharedData[getSharedDataUniqueName(this.name, 'selectable')]
    }
  },
  components: {
    DisplayPercentageComponent
  },
  watch: {
    barInfos: {
      immediate: true,
      handler(newValue: BarInfo[]) {
        if (newValue !== undefined && newValue.length != 0) {
          this.picked = newValue[0].barTitle
        }
      }
    }
  },
  data() {
    return {
      picked: '',
      reactiveStore: componentSharedData,
      selectPossibilityPoll: undefined as undefined | PollUntilSuccessPOST
    }
  },
  unmounted() {
    this.selectPossibilityPoll?.clear()
  },
  methods: {
    emitClicked() {
      PollUntilSuccessPOST.startPoll(
        this,
        'selectPossibilityPoll',
        `${this.backendAddress}/${this.address}`,
        this.processResponse.bind(this),
        { token: this.picked }
      )
    },
    processResponse(response: any) {
      this.$elementRegistry.retrieveElementsFromResponse(response, this.reactiveStore)
    }
  }
})

export default component

export function registerElement(formatter: Formatter) {
  formatter.registeredElements['softmax'] = {
    component: shallowRef(component),
    process: processElementDescr
  }
}

function processElementDescr(elementDescr: ElementDescription) {
  configurationRequired(elementDescr)
  valuesRequiredInConfiguration(elementDescr.configuration, ['address', 'bar_infos', 'long_contexts', 'names'])

  return {
    address: elementDescr.configuration.address,
    barInfos: elementDescr.configuration.bar_infos,
    longContexts: elementDescr.configuration.long_contexts,
    names: elementDescr.configuration.names,
    selectable: elementDescr.configuration.selectable,
  }
}
</script>

<style scoped>
.input-radio {
  margin-right: 10px;
}

.progress-bar {
  margin-top: 10px;
}
</style>
