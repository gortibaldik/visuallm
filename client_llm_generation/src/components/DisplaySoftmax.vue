<script lang="ts" scoped>
import { defineComponent } from 'vue';
declare const process: {
  env: {
    [key: string]: string;
  };
};

export default defineComponent({
  data() {
    return {
      softmax: [
        {token: "", prob: 100}
      ],
      picked: "",
      currentContext: "",
      pollingInterval: 1,
      howOftenToPollMs: 1000,
      backendAddress: ""
    };
  },
  methods: {
    startPollingServer() {
      this.pollingInterval = setInterval(this.pollBackend.bind(this), this.howOftenToPollMs)
    },
    async pollBackend() {
      let response;
      try {
        response = await fetch(
          `${this.backendAddress}/fetch`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
            }
          }).then(response => response.json())
        if (response.result == "success") {
          clearInterval(this.pollingInterval)
          this.currentContext = response.context
          this.softmax = response.continuations
          this.picked = this.softmax[0].token
        }        
      } catch(err) {
        console.log("Some error - poll backend")
        return
      }
    },
    async selectNextToken() {
      let response;
      try { 
        response = await fetch(
          `${this.backendAddress}/select`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              token: this.picked
            })
        }). then(response => response.json())

        if (response.result == "success") {
          this.currentContext = response.context
          this.softmax = response.continuations
          this.picked = this.softmax[0].token
        }
      } catch (err) {
        console.log("Some error - select")
        return
      }
    }
  },
  created() {
    this.backendAddress = import.meta.env.VITE_API_URL;
    this.startPollingServer()
  }
});
</script>

<template>
<div class="horizontal rounded">
  <h2>Generation with Language Models</h2>
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
