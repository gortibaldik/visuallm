<script lang="ts" scoped>
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      softmax: [
          {word: "w1", prob: 10},
          {word: "w2", prob: 20},
          {word: "w3", prob: 30},
          {word: "w4", prob: 40},
          {word: "w5", prob: 50},
          {word: "w6", prob: 60},
          {word: "w7", prob: 70},
          {word: "w8", prob: 80},
          {word: "w9", prob: 90},
          {word: "w10", prob: 100},
      ],
      picked: "",
      generatedUntilNow: "really nice text from language model",
    };
  },
});
</script>

<template>
<div class="horizontal rounded">
  <h2>Generation with Language Models</h2>
  <h3>Generated until now: </h3>
  <div style="margin-top: 10px">"{{ generatedUntilNow }}"</div>
  <h3>Possible continuations: </h3>
  <div v-for="item in softmax" class="progress-bar">
    <!-- <span class="word word-text" style="display: inline-block">{{ item.word }}</span> -->
    <span class="word-text">{{ item.word }}</span>
    <span class="progress-track">
      <div :style="{width: item.prob.toString() + '%'}" class="progress-fill">
        <span class="prob-text">{{item.prob}}%</span>
      </div>
    </span>
    <input type="radio" v-model="picked" :value="item.word">
  </div>
</div>
<div style="text-align: center; margin-top: 10px"><button style="padding: 5px">Select {{ picked }}</button></div>
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
  /* padding-left: 5px; */
}

.rounded .progress-track,
.rounded .progress-fill {
  box-shadow: inset 0 0 5px rgba(0,0,0,.2);
  border-radius: 3px;
}

</style>
