<template>
  <div :class="{ 'sample-selector': true, wrapElement: true, focused: isFocused, 'selector-wrapper': true }">
    <span class="selector-text"> {{ text }} </span>
    <span class="selector">
      <input :style="{ width: inputWidth }" type="number" :min="min" :max="max" v-model="selected" :step="stepSize"
        @focus="isFocused = true" @blur="isFocused = false" />
    </span>
  </div>
</template>

<script lang="ts">
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { numberWidth } from '@/assets/utils'
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
    stepSize(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'stepSize')]
    },
    defaultSelected(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'defaultSelected')]
    },
    text(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'text')]
    },
    inputWidth(): string {
      return numberWidth(this.selected).toString() + "px"
    }
  },
  data() {
    return {
      reactiveStore: componentSharedData,
      selected: 0 as number,
      isFocused: false as boolean,
    }
  },
  watch: {
    selected: {
      handler(new_value: number) {
        this.selected = Math.max(Math.min(new_value, this.max), this.min)
        let nameSelected = getSharedDataUniqueName(this.name, "selected")
        componentSharedData[nameSelected] = this.selected
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
  let requiredValues = { min: 'min', max: 'max', selected: 'defaultSelected', text: 'text', step_size: 'stepSize' } as { [key: string]: string }
  valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))

  let data = assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
  console.log(data)
  return data
}
</script>
<style scoped>
.selector {
  width: fit-content;
  display: inline-block;
  padding-top: 8px;
}

.selector-text {
  padding-top: 8px;
}

.selector-wrapper {
  display: flex;
}
</style>
