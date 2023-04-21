<template>
  <div class="sample-selector">
    Select dataset sample to display:
    <input type="number" :min="min" :max="max" v-model="sample_n" />
    <button class="button" @click="emitClicked()">Select</button>
  </div>
</template>

<script lang="ts">
import { convertName, contentContextRequired, valsContextContentRequired } from '@/assets/formatter'
import { reactiveStore } from '@/assets/reactiveData'
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
      return reactiveStore[convertName(this.name, 'max')]
    },
    min(): number {
      return reactiveStore[convertName(this.name, 'min')]
    },
    defaultSelected(): number {
      return reactiveStore[convertName(this.name, 'defaultSelected')]
    }
  },
  emits: ['clicked-select'],
  data() {
    return {
      reactiveStore,
      sample_n: 0 as number
    }
  },
  watch: {
    sample_n(new_value: number) {
      this.sample_n = Math.max(Math.min(Math.round(new_value), this.max), this.min)
    },
    defaultSelected: {
      handler(newValue: number) {
        this.sample_n = newValue
      },
      immediate: true
    }
  },
  methods: {
    emitClicked() {
      this.$emit('clicked-select', { sample_n: this.sample_n })
    }
  }
})

export default component

let subtype = 'min_max'
export { subtype }

export function checkSubtype(context: any, subtype: string) {
  if (context.content.subtype != subtype) {
    throw RangeError('Invalid subtype of context.content')
  }
}

export function processContext(context: any) {
  contentContextRequired(context)
  valsContextContentRequired(context, ['subtype', 'min', 'max', 'selected'])
  checkSubtype(context, subtype)
  return {
    min: context.content.min,
    max: context.content.max,
    defaultSelected: context.content.selected
  }
}
</script>
