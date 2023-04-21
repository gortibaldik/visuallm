<template>
  <div v-for="item in possibilities" class="progress-bar">
    <input v-if="selectable" class="input-radio" type="radio" v-model="picked" :value="item.content" />
    <DisplayPercentageComponent style="display: inline-block; width: 90%" :item="item" :longContexts="longContexts"
      :names="names">
    </DisplayPercentageComponent>
  </div>
  <div v-if="selectable" style="text-align: center; margin-top: 10px">
    <button class="button" @click="emitClicked()">Select "{{ picked }}"</button>
  </div>
</template>

<script lang="ts" scoped>
import { shallowRef } from 'vue'
import { defineComponent } from 'vue'
import { reactiveStore } from '@/assets/reactiveData'
import { convertName, contentContextRequired, valsContextContentRequired } from '@/assets/formatter'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'
import DisplayPercentageComponent from './DisplayPercentageComponent.vue'
import type { Item as PercentageItem } from './DisplayPercentageComponent.vue'

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  inject: ['backendAddress'],
  computed: {
    possibilities(): PercentageItem[] {
      return reactiveStore[convertName(this.name, 'possibilities')]
    },
    address(): string {
      return reactiveStore[convertName(this.name, 'address')]
    },
    names(): string[] {
      return reactiveStore[convertName(this.name, 'names')]
    },
    longContexts(): boolean {
      return reactiveStore[convertName(this.name, 'longContexts')]
    },
    selectable(): boolean {
      return reactiveStore[convertName(this.name, 'selectable')]
    }
  },
  components: {
    DisplayPercentageComponent
  },
  watch: {
    possibilities: {
      immediate: true,
      handler(newValue: PercentageItem[]) {
        if (newValue !== undefined && newValue.length != 0) {
          this.picked = newValue[0].content
        }
      }
    }
  },
  data() {
    return {
      picked: '',
      reactiveStore,
      selectPossibilityPoll: undefined as undefined | PollUntilSuccessPOST
    }
  },
  unmounted() {
    this.selectPossibilityPoll?.clear()
  },
  methods: {
    emitClicked() {
      PollUntilSuccessPOST.startPoll(
        this,
        'selectPossibilityPoll',
        `${this.backendAddress}/${this.address}`,
        this.setContexts.bind(this),
        { token: this.picked }
      )
    },
    setContexts(response: any) {
      this.$formatter.processResponse(response, this.reactiveStore)
    }
  }
})

export default component

export function registerComponent(formatter: any) {
  formatter.registeredComponents['softmax'] = {
    component: shallowRef(component),
    process: processContext
  }
}

function processContext(context: any) {
  contentContextRequired(context)
  valsContextContentRequired(context, ['address', 'possibilities', 'long_contexts', 'names'])

  return {
    address: context.content.address,
    possibilities: context.content.possibilities,
    longContexts: context.content.long_contexts,
    names: context.content.names,
    selectable: context.content.selectable,
  }
}
</script>

<style scoped>
.input-radio {
  margin-right: 10px;
}

.progress-bar {
  margin-top: 10px;
}
</style>
