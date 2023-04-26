<template>
  <span>
    <span v-if="longContexts" class="context-text" @mouseover="showProbs = true" @mouseleave="showProbs = false">"{{
      content }}"</span>
    <span v-else class="word-text">"{{ content }}"</span>
    <component :is="componentType" v-if="!longContexts || showProbs">
      <span v-for="(probability, i) in probabilities" class="prob-block" :style="{ width: progressTrackWidth }">
        <div v-if="longContexts && showProbs" class="prob-block-text">{{ names[i] }}</div>
        <span class="progress-track rounded">
          <span :style="{ width: probability.toString() + '%' }" class="progress-fill rounded">
            <span class="prob-text">{{ probability.toFixed(2) }}%</span>
          </span>
        </span>
      </span>
    </component>
  </span>
</template>

<script lang="ts" scoped>
import type { PropType } from 'vue'
import { defineComponent } from 'vue'

export interface BarInfo {
  barHeights: number[]
  barTitle: string
}

let component = defineComponent({
  props: {
    item: {
      type: Object as PropType<BarInfo>,
      required: true
    },
    longContexts: {
      type: Boolean,
      required: true
    },
    names: {
      type: Object as PropType<string[]>,
      required: true
    }
  },
  data() {
    return {
      showProbs: false
    }
  },
  computed: {
    content() {
      return this.item.barTitle
    },
    probabilities() {
      return this.item.barHeights
    },
    componentType() {
      if (this.longContexts) {
        return "div"
      } else {
        return "span"
      }
    },
    progressTrackWidth(): string {
      let oneTrackWidth = 90
      if (this.probabilities.length > 1) {
        oneTrackWidth = 100
        oneTrackWidth -= this.probabilities.length * 2
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
.prob-block {
  display: inline-block;
  padding-top: 1px;
  padding-bottom: 1px;
  margin-left: 5px;
  display: inline-block;
}

.prob-block-text {
  font-size: small;
  text-align: center;
  color: rgba(117, 117, 117, 0.533)
}

.progress-track {
  display: inline-block;
  background: #ebebeb;
  width: 100%
}

.progress-fill {
  background: #666;
  display: inline-block;
}

.prob-text {
  color: azure;
  margin-left: 2px;
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

.context-text {
  width: 100%;
  overflow: auto;
  font-size: large;
  background-color: rgb(224, 224, 224);
  padding: 5px;
}
</style>
