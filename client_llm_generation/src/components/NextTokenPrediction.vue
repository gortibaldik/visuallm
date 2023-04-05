<script lang="ts" scoped>
import { defineComponent } from 'vue';
import { PollUntilSuccessGET, PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib';


export default defineComponent({
  data() {
    return {
      softmax: [
        {token: "", prob: 100}
      ],
      picked: "",
      currentContext: "",
      tryPoll: undefined as PollUntilSuccessGET | undefined,
      selectPoll: undefined as PollUntilSuccessPOST | undefined
    };
  },
  inject: ['backendAddress'],
  created() {
    this.tryPoll = new PollUntilSuccessGET(
      `${this.backendAddress}/fetch`,
      this.setUpContext.bind(this),
      1000
    )
    this.tryPoll.newRequest()
  },
  unmounted() {
    this.tryPoll?.clear()
    this.selectPoll?.clear()
  },
  methods: {
    setUpContext(response: any) {
      this.currentContext = response.context
      this.softmax = response.continuations
      this.picked = this.softmax[0].token
    },
    async selectNextToken() {
      if (this.selectPoll == undefined) {
        this.selectPoll = new PollUntilSuccessPOST(
          `${this.backendAddress}/select`,
          this.setUpContext.bind(this),
          500,
          { token: this.picked }
        )
      } else {
        this.selectPoll.body = { token: this.picked }
      }
      this.selectPoll.newRequest()
    }
  },
});
</script>

<template>
<div class="horizontal rounded">
  <h2>Next Token Prediction</h2>
  <h3>Current Context: </h3>
  <div style="margin-top: 10px" v-html="currentContext"></div>
  <h3>Possible continuations: </h3>
  <div v-for="item in softmax" class="progress-bar">
    <!-- <span class="word word-text" style="display: inline-block">{{ item.word }}</span> -->
    <span class="word-text">"{{ item.token }}"</span>
    <span class="progress-track">
      <div :style="{width: item.prob.toString() + '%'}" class="progress-fill">
        <span class="prob-text">{{(Math.round(item.prob * 100) / 100).toFixed(2)}}%</span>
      </div>
    </span>
    <input type="radio" v-model="picked" :value="item.token">
  </div>
</div>
<div style="text-align: center; margin-top: 10px"><button style="padding: 5px" @click="selectNextToken">Select "{{ picked }}"</button></div>
</template>

<style scoped>

input {
  margin-left: 5px;
}

.progress-bar {
  margin-top: 10px;
}

.prob-text {
  color:azure;
  margin-left: 2px;
  margin-right: 2px;
}

.word-text {
  display: inline-block;
  width: 20%;
  overflow: auto;
  margin-bottom: -7px;
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
