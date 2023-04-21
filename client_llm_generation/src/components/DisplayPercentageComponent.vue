<template>
  <span>
    <span v-if="shortContent" class="word-text">"{{ content }}"</span>
    <span v-if="longContent" class="word-text">LONG: {{ content }}</span>
    <span :style="{ width: progressTrackWidth }" class="progress-track rounded">
      <div :style="{ width: probability.toString() + '%' }" class="progress-fill rounded">
        <span class="prob-text">{{ probability.toFixed(2) }}%</span>
      </div>
    </span>
  </span>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue'

let component = defineComponent({
  props: {
    probability: {
      type: Number,
      required: true
    },
    content: String
  },
  computed: {
    progressTrackWidth(): string {
      if (this.content === undefined) {
        return '100%'
      } else {
        return '90%'
      }
    },
    contentDefined(): boolean {
      return this.content !== undefined
    },
    shortContent(): boolean {
      return this.content !== undefined && !this.content.includes(' ')
    },
    longContent(): boolean {
      return this.content !== undefined && this.content.includes(' ')
    }
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
