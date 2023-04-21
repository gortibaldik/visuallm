<template>
  <div v-for="item in possibilities" class="progress-bar">
    <DisplayPercentageComponent
      style="display: inline-block; width: 90%"
      :probability="item.prob"
      :content="item.token"
    ></DisplayPercentageComponent>
    <input class="input-radio" type="radio" v-model="picked" :value="item.token" />
  </div>
  <div style="text-align: center; margin-top: 10px">
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

let component = defineComponent({
  props: {
    name: {
      type: String,
      required: true
    }
  },
  inject: ['backendAddress'],
  computed: {
    possibilities(): { token: string; prob: number }[] {
      return reactiveStore[convertName(this.name, 'possibilities')]
    },
    address(): string {
      return reactiveStore[convertName(this.name, 'address')]
    }
  },
  components: {
    DisplayPercentageComponent
  },
  watch: {
    possibilities: {
      immediate: true,
      handler(newValue: { token: string; prob: number }[]) {
        if (newValue !== undefined && newValue.length != 0) {
          this.picked = newValue[0].token
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
  valsContextContentRequired(context, ['address', 'possibilities'])

  return {
    address: context.content.address,
    possibilities: context.content.possibilities
  }
}
</script>

<style scoped>
.input-radio {
  margin-left: 5px;
}
.progress-bar {
  margin-top: 10px;
}
</style>
