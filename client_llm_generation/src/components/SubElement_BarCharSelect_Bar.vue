<template>
  <span>
    <!-- This is the annotation over whole bar -->
    <span v-if="useInlineLayout" class="word-text">"{{ content }}"</span>
    <span v-else class="context-text" @mouseover="showProbs = true" @mouseleave="showProbs = false">"{{
      content }}"</span>

    <!-- this is the bar in inline setting-->
    <span v-if="useInlineLayout" :style="{ width: trackWidth }" class="inline-bar-block">
      <span class="track rounded">
        <span :style="{ width: barWidth(probabilities[0]) }" class="track-fill rounded">
          <span class="prob-text">{{ probabilities[0].toFixed(2) }}%</span>
        </span>
      </span>
    </span>

    <div v-else class="multiline-bar-block" :style="{ width: trackWidth }">
      <span v-for="(probability, i) in probabilities" class="single-bar-wrapper">
        <div class="inline-bar-block-text"> {{ names[i] }}</div>
        <div class="track rounded">
          <div :style="{ width: barWidth(probability) }" class="track-fill rounded">
            <span class="prob-text">{{ probability.toFixed(2) }}%</span>
          </div>
        </div>
      </span>
    </div>
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
    useInlineLayout() {
      return (!this.longContexts) && (this.item.barHeights.length == 1)
    },
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
    trackWidth(): string {
      let oneTrackWidth = 90
      if (!this.useInlineLayout) {
        oneTrackWidth = 100
      }
      let width = `${oneTrackWidth}%`
      return width
    },
  },
  methods: {
    barWidth(probability: number): string {
      return probability.toString() + '%'
    },
  }
})
export default component
</script>

<style scoped>
.inline-bar-block {
  display: inline-block;
  padding-top: 1px;
  padding-bottom: 1px;
  margin-left: 5px;
}

.inline-bar-block-text {
  font-size: small;
  text-align: center;
  color: rgba(117, 117, 117, 0.533)
}

.multiline-bar-block {
  display: flex;
  column-gap: 10px;
  margin-top: 5px;
  flex-wrap: wrap;
}

.track {
  display: inline-block;
  background: #ebebeb;
  width: 100%
}

.track-fill {
  background: #666;
  display: inline-block;
  height: 100%
}

.prob-text {
  color: azure;
  margin-left: 2px;
}

.rounded .track,
.rounded .track-fill {
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

.single-bar-wrapper {
  width: 200px;
  flex-grow: 1;
}
</style>
