<template>
  <span v-if="heading">
    <h1 v-if="headingLevel === 1">{{ value }}</h1>
    <h2 v-else-if="headingLevel === 2">{{ value }}</h2>
    <h3 v-else-if="headingLevel === 3">{{ value }}</h3>
    <h4 v-else-if="headingLevel === 4">{{ value }}</h4>
    <h5 v-else-if="headingLevel === 5">{{ value }}</h5>
    <h6 v-else-if="headingLevel === 6">{{ value }}</h6>
  </span>
  <div v-else class="wrapElement plainText" v-html="value"></div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import { registerElementBase } from '@/assets/elementRegistry'
import { isSane } from '@/assets/stringMethods'

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
      let candidateValue = dataSharedInComponent[getSharedDataUniqueName(this.name, 'value')] as string
      if (!isSane(candidateValue)) {
        throw Error("Invalid value arrived from backend")
      }
      return candidateValue
    }
  },
})

export default component
/**
 * FEBEMapping is an object where key is the name of the config
 * on the backend side and value is the name of the config on the
 * frontend side.
 */
let FEBEMapping: { [key: string]: string } = {
  value: "value",
  heading: "heading",
  heading_level: "headingLevel"
}

export function registerElement(elementRegistry: ElementRegistry) {
  registerElementBase(elementRegistry, "plain", "PlainText", FEBEMapping)
}

</script>
