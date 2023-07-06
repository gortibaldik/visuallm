<template>
  <div class="wrapElement">
    <div v-for="barInfo in barInfos" class="progress-bar">
      <input v-if="selectable" class="input-radio" type="radio" v-model="selected" :value="barInfo.barTitle" />
      <DisplayPercentageComponent :style="{ display: 'inline-block', width: percentageElementWidth }" :item="barInfo"
        :longContexts="longContexts" :names="names" :maxTextWidth="maxTextWidth">
      </DisplayPercentageComponent>
    </div>
    <div v-if="selectable" style="text-align: center; margin-top: 10px">
      <button class="button" @click="emitClicked()">Select "{{ selected }}"</button>
    </div>
  </div>
</template>

<script lang="ts" scoped>
import { shallowRef } from 'vue'
import { defineComponent } from 'vue'
import { componentSharedData, getSharedDataUniqueName } from '@/assets/reactiveData'
import type Formatter from '@/assets/elementRegistry'
import { ElementDescription } from '@/assets/elementRegistry'
import { configurationRequired, valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import DisplayPercentageComponent from './SubElement_BarCharSelect_Bar.vue'
import type { BarInfo } from './SubElement_BarCharSelect_Bar.vue'
import { stringWidth } from '@/assets/utils'

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
    },

    percentageElementWidth(): string {
      if (this.selectable === true) {
        return "90%"
      } else {
        return "100%"
      }
    },
    maxTextWidth(): string {
      let maxWidth = 0
      for (let barInfo of this.barInfos) {
        let width = stringWidth(barInfo.barTitle)
        if (width > maxWidth) {
          maxWidth = width
        }
      }
      return maxWidth.toString() + "px"
    },
  },
  components: {
    DisplayPercentageComponent
  },
  watch: {
    barInfos: {
      immediate: true,
      handler(newValue: BarInfo[]) {
        if (newValue !== undefined && newValue.length != 0) {
          this.selected = newValue[0].barTitle
        }
      }
    }
  },
  data() {
    return {
      selected: '',
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
        { selected: this.selected }
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

class ElementConfiguration extends ElementDescription {
  address!: string
  bar_infos!: any
  long_contexts!: any
  names!: any
  selectable!: boolean
}

function processElementDescr(elementDescr: ElementConfiguration) {
  valuesRequiredInConfiguration(elementDescr, ['address', 'bar_infos', 'long_contexts', 'names', 'selectable'])

  return {
    address: elementDescr.address,
    barInfos: elementDescr.bar_infos,
    longContexts: elementDescr.long_contexts,
    names: elementDescr.names,
    selectable: elementDescr.selectable,
  }
}
</script>

<style scoped>
.input-radio {
  margin-right: 10px;
}

.progress-bar {
  margin-top: 10px;
  display: flex;
}
</style>
