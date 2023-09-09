<template>
  <div :class="{ 'sample-selector': true, 'wrapElement': true, focused: isFocused, 'multi-select-wrapper': true }"
    @focus="outerDivFocused = true" @blur="outerDivFocused = false" ref="content_wrapper" tabindex="0"
    @keydown.self.down.prevent="arrowDown" @keydown.self.up.prevent="arrowUp" @keydown.self.space="spacePressed">
    <span class="multi-select-inline multi-select-text">{{ text }}</span>
    <VueMultiselect ref="multiselect" @open="innerSelectFocused = true" @select="onSelect" @remove="onRemove"
      @close="onClose" class="multi-select-inline" v-model="selected" :options="choices" :placeholder="selected"
      deselectLabel="" selectLabel="" openDirection="bottom" :close-on-select="true" :tabindex="-1">
    </VueMultiselect>
  </div>
</template>

// TODO: arrows change selected in outerDivFocused regime
<script lang="ts">
import VueMultiselect from 'vue-multiselect'
import { stringWidth } from '@/assets/utils'
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { componentSharedData, getSharedDataUniqueName, assignRequiredValuesToSharedData } from '@/assets/reactiveData'
import { defineComponent } from 'vue'

interface multiselectMixin {
  filteredOptions: string[]
  pointer: number
  activate(): any
  deactivate(): any
  select(value: string): any
}

interface Focusable {
  focus(): any
}

let component = defineComponent({
  components: {
    VueMultiselect
  },
  props: {
    name: {
      type: String,
      required: true
    }
  },
  emits: ['submit'],
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
      return stringWidth(this.selected).toString() + "px"
    },
    isFocused(): boolean {
      return this.innerSelectFocused || this.outerDivFocused
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
        // save the newly selected value into the shared data
        this.selected = new_value
        let nameSelected = getSharedDataUniqueName(this.name, "selected")
        componentSharedData[nameSelected] = this.selected
      },
      immediate: true
    }
  },
  data() {
    return {
      reactiveStore: componentSharedData,
      selected: '' as string,
      outerDivFocused: false as boolean,
      innerSelectFocused: false as boolean,
    }
  },
  methods: {
    /**
     * spacePressed()
     * - if the outer div is focused then space switches the focus to the inner select
     */
    spacePressed() {
      let multiselectRef = this.$refs.multiselect as multiselectMixin

      if (!this.outerDivFocused) {
        return
      }
      this.selected = multiselectRef.filteredOptions[multiselectRef.pointer]
      multiselectRef.deactivate()
      this.outerDivFocused = false
      setTimeout(multiselectRef.activate, 5)
    },
    /** (gortibaldik) BEWARE, WEIRD HACK SECTION
     *
     * There is a need to recognize different events that can happen and due to VueMultiselect library
     * deficiencies, I have hacked it in a weird way to function just as I expect it to.
     *
     * Setup:
     * - the dropdown is opened
     *
     * Workflow 1:
     * - user selects some non-selected value
     * - select event is triggered
     * - **the library sets this.innerSelectFocused to false**
     * - **the library sets on next tick the focus event on the outer div**
     * - dropdown is closed -> close event is triggered
     * - **the library sets this.outerDivFocused to false, now nothing is
     *    focused**
     * - next tick -> outerDiv is focused
     *
     * Workflow 2:
     * - user selects already selected value
     * - remove event is triggered
     * - **library sets on next tick workflow 1**
     * - dropdown is closed -> close event is triggered
     * - **the library sets this.outerDivFocused to false, now nothing
     *    is focused**
     *
     * Workflow 3:
     * - user clicks somewhere else / presses tab
     * - dropdown is closed -> close event is triggered
     * - **the library sets this.outerDivFocused to false, now nothing is focused**
     *
     * This allows us to distinguish the 3 possible actions taken by user, the result
     * is deterministic and doesn't depend on the internal ordering of events. (thanks
     * to the nextTick)
     */



    /** Workflow 3
     */
    onClose() {
      this.outerDivFocused = false
      this.innerSelectFocused = false
    },
    switchFocusToOuterDiv() {
      this.innerSelectFocused = false

      let contentWrapper = this.$refs.content_wrapper as Focusable

      if (contentWrapper === undefined) {
        return
      }

      this.$nextTick(() => {
        contentWrapper.focus()
      })
    },
    /** Workflow 1
     */
    onSelect() {
      this.innerSelectFocused = false
      this.outerDivFocused = true
      this.switchFocusToOuterDiv()
    },
    /** Workflow 2
     */
    onRemove(removedOption: string, id: any) {
      this.innerSelectFocused = false
      let multiselectRef = this.$refs.multiselect as multiselectMixin
      this.$nextTick(() => {
        multiselectRef.select(removedOption)
      })
    },
    arrowUp() {
      console.log("arrowUp")
      let multiselectRef = this.$refs.multiselect as multiselectMixin
      if (multiselectRef === undefined) {
        console.log("multiselectref undefined")
        return
      }
      let len = multiselectRef.filteredOptions.length
      if (multiselectRef.pointer == 0) {
        multiselectRef.pointer = len - 1
      } else {
        multiselectRef.pointer -= 1
      }
      multiselectRef.select(multiselectRef.filteredOptions[multiselectRef.pointer])
    },
    arrowDown() {
      console.log("arrowDown")
      let multiselectRef = this.$refs.multiselect as multiselectMixin
      if (multiselectRef === undefined) {
        console.log("multiselectRef Undefined")
        return
      }
      let len = multiselectRef.filteredOptions.length
      if (multiselectRef.pointer == len - 1) {
        multiselectRef.pointer = 0
      } else {
        multiselectRef.pointer += 1
      }
      multiselectRef.select(multiselectRef.filteredOptions[multiselectRef.pointer])
    },
  },
})

export default component

let subtype = 'choices'
export { subtype }

// TODO documentation
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

<style src="vue-multiselect/dist/vue-multiselect.css"></style>

<style scoped>
.multi-select-inline {
  flex-basis: auto;
  white-space: nowrap;
}

.multi-select-text {
  padding-top: 8px;
  margin-right: 4px;
}

.multi-select-wrapper {
  display: flex;
  flex-direction: row;
}
</style>
