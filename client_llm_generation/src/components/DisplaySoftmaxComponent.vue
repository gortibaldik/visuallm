<template>
    <div v-for="item in softmax" class="progress-bar">
        <span class="word-text">"{{ item.token }}"</span>
        <span class="progress-track">
            <div :style="{ width: item.prob.toString() + '%' }" class="progress-fill">
                <span class="prob-text">{{ (Math.round(item.prob * 100) / 100).toFixed(2) }}%</span>
            </div>
        </span>
        <input class="input-radio" type="radio" v-model="picked" :value="item.token">
    </div>
    <div style="text-align: center; margin-top: 10px"><button class="button" style="padding: 5px" @click="$emit('picked-softmax', picked)">Select "{{ picked }}"</button></div>
</template>

<script lang="ts" scoped>
import { shallowRef } from 'vue';
import { defineComponent } from 'vue';

class Data {
    value: {token: string, prob: number}[]
    constructor(value: {token: string, prob:number}[]) {
        this.value = value
    }
}

let component = defineComponent({
    props: {
        passed_data: {
            type: Data,
            required: true
        }
    },
    watch: {
      passed_data(newValue: Data) {
        console.log("passed data updated!")
        this.softmax = newValue.value
        this.picked = newValue.value[0].token
      },
    },
    mounted() {
      console.log("mounted")
      this.update_data()
    },
    emits: ['picked-softmax'],
    data() {
        return {
            softmax: this.passed_data.value,
            picked: this.passed_data.value[0].token
        }
    },
    methods: {
      update_data() {
        console.log("Updating data")
        console.log(this.passed_data)
        this.softmax = this.passed_data.value
        this.picked = this.passed_data.value[0].token
        console.log(this.softmax, this.picked)
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
    return new Data(context.content)
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