<template>
  <span>
    <span v-if="isLong" class="word-text">LONG: "{{ content }}"</span>
    <span v-else class="word-text">"{{ content }}"</span>
    <span v-for="probability in probabilities" :style="{ width: progressTrackWidth }" class="progress-track rounded">
      <div :style="{ width: probability.toString() + '%' }" class="progress-fill rounded">
        <span class="prob-text">{{ probability.toFixed(2) }}%</span>
      </div>
    </span>
  </span>
</template>

<script lang="ts" scoped>
import type { PropType } from 'vue'
import { defineComponent } from 'vue'

export interface Item {
  probs: number[]
  content: string
  is_long: boolean
}

let component = defineComponent({
  props: {
    item: {
      type: Object as PropType<Item>,
      required: true
    },
  },
  computed: {
    content() {
      return this.item.content
    },
    probabilities() {
      return this.item.probs
    },
    isLong() {
      let long_enforced = this.item.is_long
      long_enforced ||= this.probabilities.length > 1
      return long_enforced
    },
    progressTrackWidth(): string {
      let oneTrackWidth = 90
      if (this.probabilities.length > 1) {
        oneTrackWidth -= this.probabilities.length
        oneTrackWidth /= this.probabilities.length
      }
      let width = `${oneTrackWidth}%`
      return width
    },
  }
})
export default component
</script>

<style scoped>
.progress-track {
  background: #ebebeb;
  display: inline-block;
  padding-top: 1px;
  padding-bottom: 1px;
}

.progress-fill {
  background: #666;
}

.prob-text {
  color: azure;
  margin-left: 2px;
  margin-right: 2px;
}

.rounded .progress-track,
.rounded .progress-fill {
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.word-text {
  display: inline-block;
  width: 8%;
  overflow: auto;
  margin-bottom: -7px;
  margin-right: 5px;
}
</style>
