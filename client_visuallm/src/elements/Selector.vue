<template>
  <form class="wrapElement" @submit.prevent="submit" @keypress.enter="submit">
    <div class="subSelectorsWrapper">
      <component v-for="subElementConfigFE in subElementConfigurationsFE" :is="getComponent(subElementConfigFE.subtype)"
        :name="subElementConfigFE.name" @make-bigger="onMakeBigger" @make-smaller="onMakeSmaller"></component>
    </div>
    <div class="buttonWrapper">
      <button class="button" :disabled="buttonDisabled || loadingInProgress" type="submit" ref="button">{{ buttonText }}</button>
      <DesignLoading v-if="loadingInProgress" class="loading-indicator" />
    </div>
  </form>
</template>

<script lang="ts">
import DesignLoading from './utils/Design_Loading.vue'
import { defineComponent } from 'vue'
import { dataSharedInComponent, getSharedDataUniqueName, getSharedDataElementName } from '@/assets/reactiveData'
import type ElementRegistry from '@/assets/elementRegistry'
import { ElementDescription, valuesRequiredInConfiguration, entries } from '@/assets/elementRegistry'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import {
  subtype as minMaxSubtype,
  processSubElementConfiguration as minMaxProcessSubElementConfig
} from './subelements_selector/MinMaxSelector.vue'
import MinMaxSubElement from './subelements_selector/MinMaxSelector.vue'
import {
  subtype as horizontalMultiRadioSubtype,
  processSubElementConfiguration as hmrProcessSubElementConfig
} from './subelements_selector/MultiRadio.vue'
import MultiRadioSubElement from './subelements_selector/MultiRadio.vue'
import {
  subtype as choicesSubtype,
  processSubElementConfiguration as choicesProcessSubElementConfig
} from './subelements_selector/ChoicesSelector.vue'
import ChoicesSubElement from './subelements_selector/ChoicesSelector.vue'

import {
  subtype as checkboxSubtype,
  processSubElementConfiguration as checkboxProcessSubElementConfig
} from './subelements_selector/CheckBox.vue'
import CheckBoxSubElement from './subelements_selector/CheckBox.vue'


import {
  subtype as textInputSubtype,
  processSubElementConfiguration as textInputProcessSubElementConfig
} from './subelements_selector/TextInput.vue'
import TextInputSubElement from './subelements_selector/TextInput.vue'
import { computeEndingYCoordinate } from '@/assets/heightMethods'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    subElementConfigurationsFE(): SubElementConfigurationFE[] {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'subElementConfigs')]
    },
    callbackAddress(): string {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'address')]
    },
    buttonText(): string {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'buttonText')]
    },
    buttonDisabled(): boolean {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'disabled')]
    },
    reloadPage(): boolean {
      return dataSharedInComponent[getSharedDataUniqueName(this.name, 'reloadPage')]
    }
  },
  inject: ['backendAddress'],
  emits: ['makeBigger', 'makeSmaller', 'reloadPage'],
  data() {
    return {
      selectSamplePoll: undefined as undefined | PollUntilSuccessPOST,
      loadingInProgress: false as boolean,
      loadingBarId: "",
    }
  },
  unmounted() {
    this.selectSamplePoll?.clear()
  },
  created() {
    this.loadingBarId = `${this.name}>loadingBar`
  },
  components: {
    MinMaxSubElement,
    ChoicesSubElement,
    CheckBoxSubElement,
    TextInputSubElement,
    HorizontalMultiRadioSubElement: MultiRadioSubElement,
    DesignLoading,
  },
  methods: {
    submit() {
      let dataToSend = {} as { [key: string]: any }

      for (let key in Object.keys(this.subElementConfigurationsFE)) {
        let config = this.subElementConfigurationsFE[key]
        let subElementValueName = getSharedDataUniqueName(config.name, "selected")
        let subelementName = getSharedDataElementName(config.name)
        let elementValue = dataSharedInComponent[subElementValueName]

        dataToSend[subelementName] = elementValue
      }

      this.loadingInProgress = true
      let buttonHTMLElement = this.$refs.button as HTMLElement
      this.onMakeBigger(computeEndingYCoordinate(buttonHTMLElement, 36), this.loadingBarId)
      PollUntilSuccessPOST.startPoll(
        this,
        'selectSamplePoll',
        `${this.backendAddress}/${this.callbackAddress}`,
        this.setContexts.bind(this),
        dataToSend
      )
    },
    setContexts(response: any) {
      // reloadPage forces reload of all the elements, with the possibility
      // of removing or adding some of the elements. Hence the rerender of the
      // page is needed. The responsibility belongs to the `FrontendComponent`,
      // so this method only sends the response to that component and doesn't
      // mangle in any way with the dataSharedInComponent
      if (this.reloadPage) {
        this.$emit("reloadPage", response)
        return
      }

      // no reload of page is required, hence only update the values
      // of already rendered elments
      this.$elementRegistry.retrieveElementsFromResponse(response, dataSharedInComponent)
      if (this.loadingInProgress) {
        this.onMakeSmaller(this.loadingBarId)
      }
      this.loadingInProgress = false
    },
    getComponent(subtype: string) {
      let component = subElementProcessors[subtype].component
      return component
    },
    onMakeBigger(requiredEndingYCoordinate: number, idOfCaller: string) {
      this.$emit("makeBigger", requiredEndingYCoordinate, idOfCaller)
    },
    onMakeSmaller(idOfCaller: string) {
      this.$emit("makeSmaller", idOfCaller)
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
  },
  [textInputSubtype]: {
    process: textInputProcessSubElementConfig,
    component: nameof({ TextInputSubElement })
  },
  [horizontalMultiRadioSubtype]: {
    process: hmrProcessSubElementConfig,
    component: nameof({ HorizontalMultiRadioSubElement: MultiRadioSubElement })
  }
}

interface SubElementConfigurationFromBE {
  subtype: string
  name: string
  parent_name: string
  configuration: any
}

/**
 * Path to the configuration for each subelement
 *
 * - subtype is the key of the component that should render that subelement
 * - name is the unique name of the subelement in the selector element.
 */
interface SubElementConfigurationFE {
  subtype: string
  name: string
}

class ElementConfiguration extends ElementDescription {
  subelement_configs!: SubElementConfigurationFromBE[]
  address!: string
  button_text!: string
  disabled!: boolean
  reload_page!: boolean
}

export function registerElement(elementRegistry: ElementRegistry) {
  elementRegistry.registeredElements['button'] = {
    component: "Selector",
    process: processElementDescr
  }
}

function processElementDescr(configuration: ElementConfiguration) {
  valuesRequiredInConfiguration(configuration, Object.keys(ElementConfiguration))

  let data = {
    address: configuration.address,
    buttonText: configuration.button_text,
    disabled: configuration.disabled,
    reloadPage: configuration.reload_page,
    // subelement configs contain
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
  padding: 5px;
  padding-left: 10px;
  padding-right: 10px;
  /* don't resize */
  width: fit-content;
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
  display: flex;
  align-items: center;
  flex-direction: column;
  row-gap: 10px;
}
</style>
