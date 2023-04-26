<template>
  <div class="sample-selector wrapElement">
    <span class="descr">{{ text }}</span>
    <select :style="{ width: inputWidth }" v-model="selected">
      <option disabled value="">Please select one</option>
      <option v-for="option in choices">{{ option }}</option>
    </select>
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
    choices(): string[] {
      return componentSharedData[getSharedDataUniqueName(this.name, 'choices')]
    },
    defaultSelected(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'defaultSelected')]
    },
    text(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'text')]
    },
    inputWidth(): string {
      let maxWidth = this.selected.length
      maxWidth *= 7
      maxWidth += 30

      let maxWidthPx = maxWidth.toString() + "px"
      return maxWidthPx
    }
  },
  watch: {
    defaultSelected: {
      handler(newValue: string) {
        this.selected = newValue
      },
      immediate: true
    },
    selected: {
      handler(new_value: string) {
        this.selected = new_value
        let nameSelected = getSharedDataUniqueName(this.name, "selected")
        componentSharedData[nameSelected] = this.selected

        console.log(nameSelected, this.selected, componentSharedData[nameSelected])
      },
      immediate: true
    }
  },
  data() {
    return {
      reactiveStore: componentSharedData,
      selected: '' as string
    }
  },
})

export default component

let subtype = 'choices'
export { subtype }

export function processSubElementConfiguration(this_name: string, subElementConfiguration: any) {
  let requiredValues = { choices: "choices", selected: "defaultSelected", text: "text" } as { [key: string]: string }
  valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))

  if (subElementConfiguration.choices.length === 0) {
    throw RangeError('Choices cannot be of zero length')
  }

  let data = assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
  return data
}
</script>
