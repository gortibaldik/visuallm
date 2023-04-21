<template>
  <div class="sample-selector">
    <span>Select model: </span>
    <select v-model="selected">
      <option disabled value="">Please select one</option>
      <option v-for="option in choices">{{ option }}</option>
    </select>
    <button class="button" @click="emitClicked()">Select</button>
  </div>
</template>

<script lang="ts">
import { convertName, contentContextRequired, valsContextContentRequired } from '@/assets/formatter'
import { reactiveStore } from '@/assets/reactiveData'
import { defineComponent } from 'vue'
import { checkSubtype } from './DisplayMinMaxSelector.vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  computed: {
    choices(): string[] {
      return reactiveStore[convertName(this.name, 'choices')]
    },
    defaultSelected(): string {
      return reactiveStore[convertName(this.name, 'defaultSelected')]
    }
  },
  watch: {
    defaultSelected: {
      handler(newValue: string) {
        this.selected = newValue
      },
      immediate: true
    }
  },
  emits: ['clicked-select'],
  data() {
    return {
      reactiveStore,
      selected: '' as string
    }
  },
  methods: {
    emitClicked() {
      this.$emit('clicked-select', { choice: this.selected })
    }
  }
})

export default component

let subtype = 'choices'
export { subtype }

export function processContext(context: any) {
  contentContextRequired(context)
  valsContextContentRequired(context, ['choices', 'selected'])
  checkSubtype(context, subtype)

  if (context.content.choices.length === 0) {
    throw RangeError('Choices cannot be of zero length')
  }

  return {
    choices: context.content.choices,
    defaultSelected: context.content.selected
  }
}
</script>
