<template>
  <span v-if="heading">
    <h1 v-if="headingLevel === 1">{{ value }}</h1>
    <h2 v-else-if="headingLevel === 2">{{ value }}</h2>
    <h3 v-else-if="headingLevel === 3">{{ value }}</h3>
    <h4 v-else-if="headingLevel === 4">{{ value }}</h4>
    <h5 v-else-if="headingLevel === 5">{{ value }}</h5>
    <h6 v-else-if="headingLevel === 6">{{ value }}</h6>
  </span>
  <div v-else class="wrapElement">{{ value }}</div>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue'
import { componentSharedData, getSharedDataUniqueName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import type { ElementDescription } from '@/assets/elementRegistry'
import { configurationRequired, valuesRequiredInConfiguration } from '@/assets/elementRegistry'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    headingLevel(): number {
      return componentSharedData[getSharedDataUniqueName(this.name, 'headingLevel')]
    },
    heading(): boolean {
      return componentSharedData[getSharedDataUniqueName(this.name, 'heading')]
    },
    value(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'value')]
    }
  },
})

export default component
export function registerElement(formatter: ElementRegistry) {
  formatter.registeredElements['plain'] = {
    component: shallowRef(component),
    process: processElementDescr
  }
}

function processElementDescr(elementDescr: ElementDescription) {
  configurationRequired(elementDescr)
  valuesRequiredInConfiguration(elementDescr.configuration, ['value', 'heading', 'heading_level'])
  return {
    value: elementDescr.configuration.value,
    heading: elementDescr.configuration.heading,
    headingLevel: elementDescr.configuration.heading_level
  }
}
</script>
