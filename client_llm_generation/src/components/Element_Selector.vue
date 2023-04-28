<template>
  <div class="wrapElement">
    <div class="subSelectorsWrapper">
      <component v-for="subElementConfigFE in subElementConfigurationsFE" :is="getComponent(subElementConfigFE.subtype)"
        :name="subElementConfigFE.name"></component>
    </div>
    <div class="buttonWrapper">
      <button class="button" @click="emitClicked()">{{ buttonText }}</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue'
import { componentSharedData, getSharedDataUniqueName, getSharedDataElementName } from '@/assets/reactiveData'
import type Formatter from '@/assets/elementRegistry'
import type { ElementDescription } from '@/assets/elementRegistry'
import { configurationRequired, valuesRequiredInConfiguration, entries } from '@/assets/elementRegistry'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import {
  subtype as minMaxSubtype,
  processSubElementConfiguration as minMaxProcessSubElementConfig
} from './SubElement_Selector_MinMaxSelector.vue'
import MinMaxSubElement from './SubElement_Selector_MinMaxSelector.vue'
import {
  subtype as choicesSubtype,
  processSubElementConfiguration as choicesProcessSubElementConfig
} from './Subelement_Selector_ChoicesSelector.vue'
import ChoicesSubElement from './Subelement_Selector_ChoicesSelector.vue'

import {
  subtype as checkboxSubtype,
  processSubElementConfiguration as checkboxProcessSubElementConfig
} from './SubElement_Selector_CheckBox.vue'
import CheckBoxSubElement from './SubElement_Selector_CheckBox.vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    subElementConfigurationsFE(): SubElementConfigurationFE[] {
      return componentSharedData[getSharedDataUniqueName(this.name, 'subElementConfigs')]
    },
    callbackAddress(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'callbackAddress')]
    },
    buttonText(): string {
      return componentSharedData[getSharedDataUniqueName(this.name, 'buttonText')]
    }
  },
  inject: ['backendAddress'],
  data() {
    return {
      reactiveStore: componentSharedData,
      selectSamplePoll: undefined as undefined | PollUntilSuccessPOST
    }
  },
  unmounted() {
    this.selectSamplePoll?.clear()
  },
  components: {
    MinMaxSubElement,
    ChoicesSubElement,
    CheckBoxSubElement,
  },
  methods: {
    emitClicked() {
      let dataToSend = {} as { [key: string]: any }

      for (let key in Object.keys(this.subElementConfigurationsFE)) {
        let config = this.subElementConfigurationsFE[key]
        let subElementValueName = getSharedDataUniqueName(config.name, "selected")
        let elementName = getSharedDataElementName(config.name)
        let elementValue = componentSharedData[subElementValueName]
        console.log("selected subElement:", elementName, elementValue)

        dataToSend[elementName] = elementValue
      }

      PollUntilSuccessPOST.startPoll(
        this,
        'selectSamplePoll',
        `${this.backendAddress}/${this.callbackAddress}`,
        this.setContexts.bind(this),
        dataToSend
      )
    },
    setContexts(response: any) {
      this.$elementRegistry.retrieveElementsFromResponse(response, this.reactiveStore)
    },
    getComponent(subtype: string) {
      let component = subElementProcessors[subtype].component
      console.log(subtype, component)
      return component
    }
  }
})

export default component

function nameof(variable: any) {
  return Object.keys(variable)[0]
}

let subElementProcessors = {
  [minMaxSubtype]: {
    process: minMaxProcessSubElementConfig,
    component: nameof({ MinMaxSubElement })
  },
  [choicesSubtype]: {
    process: choicesProcessSubElementConfig,
    component: nameof({ ChoicesSubElement })
  },
  [checkboxSubtype]: {
    process: checkboxProcessSubElementConfig,
    component: nameof({ CheckBoxSubElement })
  }
}

interface SubElementConfigurationFromBE {
  subtype: string
  name: string
  parent_name: string
  configuration: any
}

interface SubElementConfigurationFE {
  subtype: string
  name: string
}

interface ElementConfiguration {
  subelement_configs: SubElementConfigurationFromBE[]
  address: string
  button_text: string
}

export function registerElement(formatter: Formatter) {
  formatter.registeredElements['sample_selector'] = {
    component: shallowRef(component),
    process: processElementDescr
  }
}

function processElementDescr(elementDescr: ElementDescription) {
  configurationRequired(elementDescr)
  valuesRequiredInConfiguration(elementDescr.configuration, ['subelement_configs', 'address', 'button_text'])

  let configuration: ElementConfiguration = elementDescr.configuration
  let data = {
    callbackAddress: configuration.address,
    buttonText: configuration.button_text,
    subElementConfigs: [] as SubElementConfigurationFE[]
  } as { [key: string]: any }

  for (let subElementConfiguration of configuration.subelement_configs) {
    if (!(subElementConfiguration.subtype in subElementProcessors)) {
      throw RangeError(`Wrong subtype: ${subElementConfiguration.subtype}`
        + ` not in ${Object.keys(subElementProcessors)}`)
    }
    data.subElementConfigs.push({
      name: getSharedDataUniqueName(subElementConfiguration.parent_name, subElementConfiguration.name),
      subtype: subElementConfiguration.subtype
    })

    // the keys in the object returned by process are in the form
    // [subElementConfiguration.name]>>[key_of_value]
    //
    // hence after the processing done by elementRegistry the keys of those
    // values will be [this.name]>>[subElementConfiguration.name]>>[key_of_value]
    //
    // hence if we pass [this.name]>>[subElementConfiguration.name] as a name to the
    // subcomponent, then the subcomponent will be able to access the data just by
    // getSharedDataUniqueName(this.name, key_of_value)
    let subElementProcessor = subElementProcessors[subElementConfiguration.subtype]
    let subElementData = subElementProcessor.process(subElementConfiguration.name, subElementConfiguration.configuration)
    for (let [key, value] of entries(subElementData)) {
      data[key as string] = value
    }
  }

  return data
}
</script>

<style scoped>
:deep(.sample-selector) {
  font-family: sans-serif;
  font-weight: normal;
  padding: 5px;
}

:deep(.button) {
  display: inline-block;
  padding: 5px;
  padding-left: 10px;
  padding-right: 10px;
  margin-left: 5px;
}

:deep(.descr) {
  margin-right: 5px;
}

.subSelectorsWrapper {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-evenly;
}

.buttonWrapper {
  text-align: center;
}
</style>
