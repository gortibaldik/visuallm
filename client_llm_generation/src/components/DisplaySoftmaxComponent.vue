<template>
    <div v-for="item in possibilities" class="progress-bar">
        <span class="word-text">"{{ item.token }}"</span>
        <span class="progress-track">
            <div :style="{ width: item.prob.toString() + '%' }" class="progress-fill">
                <span class="prob-text">{{ (Math.round(item.prob * 100) / 100).toFixed(2) }}%</span>
            </div>
        </span>
        <input class="input-radio" type="radio" v-model="picked" :value="item.token">
    </div>
    <div style="text-align: center; margin-top: 10px"><button class="button" @click="emitClicked()">Select "{{ picked }}"</button></div>
</template>

<script lang="ts" scoped>
import { shallowRef } from 'vue';
import { defineComponent } from 'vue';
import { reactiveStore } from '@/assets/reactiveData';
import { convertName, contentContextRequired, valsContextContentRequired } from '@/assets/formatter';
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib';


let component = defineComponent({
    props: {
        name: {
          type: String,
          required: true
        }
    },
    inject: ["backendAddress"],
    computed: {
      possibilities(): {token: string, prob: number}[] {
        return reactiveStore[convertName(this.name, "possibilities")]
      },
      address(): string {
        return reactiveStore[convertName(this.name, "address")]
      }
    },
    watch: {
      possibilities: {
        immediate: true,
        handler(newValue: {token: string, prob: number}[]){
          if ((newValue !== undefined) && (newValue.length != 0)) {
            this.picked = newValue[0].token
          }
        }
      } 
    },
    data() {
      return {
        picked: "",
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
          "selectPossibilityPoll",
          `${this.backendAddress}/${this.address}`,
          this.setContexts.bind(this),
          { token: this.picked }
        )
      },
      setContexts(response: any) {
        this.$formatter.processResponse(
          response,
          this.reactiveStore
        )
      }
    }
})

export default component

export function registerComponent(formatter: any) {
    formatter.registeredComponents["softmax"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
  contentContextRequired(context)
  valsContextContentRequired(context, ["address", "possibilities"])
  
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
.word-text {
  display: inline-block;
  width: 20%;
  overflow: auto;
  margin-bottom: -7px;
}

.prob-text {
  color:azure;
  margin-left: 2px;
  margin-right: 2px;
}

.progress-track {
  background: #ebebeb;
  width: 70%;
  display: inline-block;
  padding-top: 1px;
  padding-bottom: 1px;
}

.progress-fill {
  background: #666;
}

.rounded .progress-track,
.rounded .progress-fill {
  box-shadow: inset 0 0 5px rgba(0,0,0,.2);
  border-radius: 3px;
}
</style>