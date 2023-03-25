<script lang="ts" scoped>
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      softmax: [
        {token: "", prob: 100}
      ],
      picked: "",
      currentContext: "",
      polllingInterval: 1,
      howOftenToPollMs: 1000,
      backendAddress: ""
    };
  },
  methods: {
    startPollingServer() {
      this.polllingInterval = setInterval(this.pollBackend.bind(this), this.howOftenToPollMs)
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
          clearInterval(this.polllingInterval)
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
    this.backendAddress = "http://127.0.0.1:5000"
    this.startPollingServer()
  }
});
</script>

<template>
<div class="horizontal rounded">
  <h2>Generation with Language Models</h2>
  <h3>Current Context: </h3>
  <div style="margin-top: 10px">"{{ currentContext }}"</div>
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

h2 {
  border-bottom: 1px solid #999;
  font-family: sans-serif;
  font-weight: normal;
  color: #333;
}

h3 {
  border-bottom: 1px solid #999;
  font-family: sans-serif;
  font-weight: lighter;
  margin-top: 10px;
}

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
  width: 10%;
  overflow: auto;
  margin-bottom: -7px;
}

.progress-track {
  background: #ebebeb;
  width: 80%;
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
