<template>
  <form class="wrapElement barChartSelect" @submit.prevent="submit">
    <div v-for="(barInfo, i) in barInfos" :class="{ 'progress-bar': true, focused: focusedBarInfos[i] }">
      <input v-if="selectable" class="input-radio" type="radio" v-model="selected" :value="barInfo.pieceTitle"
        @focus="focusedBarInfos[i] = true" @blur="focusedBarInfos[i] = false" />
      <DisplayPercentageComponent :style="{ display: 'inline-block', width: percentageElementWidth }" :item="barInfo"
        :longContexts="longContexts" :maxTextWidth="maxTextWidth">
      </DisplayPercentageComponent>
    </div>
    <div v-if="selectable" style="text-align: center; margin-top: 10px">
      <button class="button" type="submit">Select "{{ selected }}"</button>
    </div>
  </form>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import { registerElementBase } from '@/assets/elementRegistry'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import DisplayPercentageComponent from './subelements_barchart/Bar.vue'
import type { PieceInfo } from './subelements_barchart/Bar.vue'
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
    barInfos(): PieceInfo[] {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'barInfos')]
    },
    /** Path to endpoint which is called when select button is pressed
     */
    address(): string {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'address')]
    },
    longContexts(): boolean {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'longContexts')]
    },
    /** Bar chart could be either treated as a selection advice, e.g. add
     * input radio before each bar and select button at the end to help user
     * make informed selection, or it can be treated solely as an information
     * panel and then no select button or input radio should be added.
     */
    selectable(): boolean {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'selectable')]
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
        let width = stringWidth(barInfo.pieceTitle)
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
      handler(newValue: PieceInfo[]) {
        if (newValue !== undefined && newValue.length != 0) {
          this.selected = newValue[0].pieceTitle
          let focusedBarInfos = [] as boolean[]
          for (let i = 0; i < newValue.length; i++) {
            focusedBarInfos.push(false)
          }
          this.focusedBarInfos = focusedBarInfos
        }
      }
    }
  },
  data() {
    return {
      selected: '',
      reactiveStore: dataSharedInComponent,
      selectPossibilityPoll: undefined as undefined | PollUntilSuccessPOST,
      focusedBarInfos: [] as boolean[]
    }
  },
  unmounted() {
    this.selectPossibilityPoll?.clear()
  },
  methods: {
    submit() {
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

let FEBEMapping: { [key: string]: string } = {
  "address": "address",
  "piece_infos": "barInfos",
  "long_contexts": "longContexts",
  "selectable": "selectable"
}

export function registerElement(elementRegistry: ElementRegistry) {
  registerElementBase(elementRegistry, "softmax", "BarChartSelect", FEBEMapping)
}

</script>

<style scoped>
.input-radio {
  margin-right: 10px;
}

.progress-bar {
  padding-top: 5px;
  padding-bottom: 5px;
  display: flex;
}
</style>
