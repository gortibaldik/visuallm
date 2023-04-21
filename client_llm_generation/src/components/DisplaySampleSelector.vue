<template>
  <component
    :is="subcomponents[subtype].component"
    :name="name"
    @clicked-select="(data: any) => emitClicked(data)"
  ></component>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue'
import { reactiveStore } from '@/assets/reactiveData'
import { convertName, contentContextRequired, valsContextContentRequired } from '@/assets/formatter'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import {
  subtype as minMaxSubtype,
  processContext as minMaxProcessContext
} from './DisplayMinMaxSelector.vue'
import MinMaxComponent from './DisplayMinMaxSelector.vue'
import {
  subtype as choicesSubtype,
  processContext as choicesProcessContext
} from './DisplayChoicesSelector.vue'
import ChoicesComponent from './DisplayChoicesSelector.vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    subtype(): string {
      return reactiveStore[convertName(this.name, 'subtype')]
    },
    callbackAddress(): string {
      return reactiveStore[convertName(this.name, 'callbackAddress')]
    }
  },
  inject: ['backendAddress'],
  data() {
    return {
      reactiveStore,
      selectSamplePoll: undefined as undefined | PollUntilSuccessPOST,
      subcomponents: subcomponents
    }
  },
  unmounted() {
    this.selectSamplePoll?.clear()
  },
  methods: {
    emitClicked(dataToSend: any) {
      PollUntilSuccessPOST.startPoll(
        this,
        'selectSamplePoll',
        `${this.backendAddress}/${this.callbackAddress}`,
        this.setContexts.bind(this),
        dataToSend
      )
    },
    setContexts(response: any) {
      this.$formatter.processResponse(response, this.reactiveStore)
    }
  }
})

export default component
export function registerComponent(formatter: any) {
  formatter.registeredComponents['sample_selector'] = {
    component: shallowRef(component),
    process: processContext
  }
}

let subcomponents = {
  [minMaxSubtype]: {
    process: minMaxProcessContext,
    component: shallowRef(MinMaxComponent)
  },
  [choicesSubtype]: {
    process: choicesProcessContext,
    component: shallowRef(ChoicesComponent)
  }
}

type Data = {
  [key: string]: any
  callbackAddress?: string
  subtype?: string
}

function processContext(context: any) {
  contentContextRequired(context)
  valsContextContentRequired(context, ['subtype', 'address'])

  let subtype = context.content.subtype
  if (!(subtype in subcomponents)) {
    throw RangeError(
      `Invalid context.content.subtype: '${subtype}' isn't supported between [-- ${Object.keys(
        subcomponents
      )} --]`
    )
  }

  let data: Data = subcomponents[context.content.subtype].process(context)
  data.callbackAddress = context.content.address
  data.subtype = context.content.subtype

  return data
}
</script>

<style scoped>
:deep(.sample-selector) {
  font-family: sans-serif;
  font-weight: normal;
}

:deep(.button) {
  display: inline-block;
  padding: 5px;
  padding-left: 10px;
  padding-right: 10px;
  margin-left: 5px;
}
</style>
