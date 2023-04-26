<template>
  <div class="sample-selector wrapElement">
    <span class="descr"> {{ text }} </span>
    <span class="selectorWrapper">
      <input :style="{ width: inputWidth }" type="number" :min="min" :max="max" v-model="selected" />
    </span>
  </div>
</template>

<script lang="ts">
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { componentSharedData, getSharedDataUniqueName, assignRequiredValuesToSharedData } from '@/assets/reactiveData'
import { defineComponent } from 'vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    max(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'max')]
    },
    min(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'min')]
    },
    defaultSelected(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'defaultSelected')]
    },
    text(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'text')]
    },
    inputWidth(): string {
      // TODO: find some better method of measuring number width
      let w = this.selected.toString().length * 7 + 35
      let ws = w.toString() + "px"
      console.log(ws)
      return ws
    }
  },
  data() {
    return {
      reactiveStore: componentSharedData,
      selected: 0 as number
    }
  },
  watch: {
    selected: {
      handler(new_value: number) {
        this.selected = Math.max(Math.min(Math.round(new_value), this.max), this.min)
        let nameSelected = getSharedDataUniqueName(this.name, "selected")
        componentSharedData[nameSelected] = this.selected

        console.log(nameSelected, this.selected, componentSharedData[nameSelected])
      },
      immediate: true
    },
    defaultSelected: {
      handler(newValue: number) {
        this.selected = newValue
      },
      immediate: true
    }
  },
})

export default component

let subtype = 'min_max'
export { subtype }

export function checkSubtype(context: any, subtype: string) {
  if (context.content.subtype != subtype) {
    throw RangeError('Invalid subtype of context.content')
  }
}

export function processSubElementConfiguration(this_name: string, subElementConfiguration: any) {
  let requiredValues = { min: 'min', max: 'max', selected: 'defaultSelected', text: 'text' } as { [key: string]: string }
  valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))

  let data = assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
  console.log(data)
  return data
}
</script>
<style scoped>
.selectorWrapper {
  width: fit-content;
  display: inline-block;
}
</style>
