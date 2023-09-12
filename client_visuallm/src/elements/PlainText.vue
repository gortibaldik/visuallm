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
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import { ElementDescription } from '@/assets/elementRegistry'
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry'

// TODO: allow custom html in the plain text element

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    headingLevel(): number {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'headingLevel')]
    },
    heading(): boolean {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'heading')]
    },
    value(): string {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'value')]
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

class ElementConfiguration extends ElementDescription {
  value!: string
  heading!: any
  heading_level!: any
}

function processElementDescr(elementDescr: ElementConfiguration) {
  valuesRequiredInConfiguration(elementDescr, ['value', 'heading', 'heading_level'])
  return {
    value: elementDescr.value,
    heading: elementDescr.heading,
    headingLevel: elementDescr.heading_level
  }
}
</script>
