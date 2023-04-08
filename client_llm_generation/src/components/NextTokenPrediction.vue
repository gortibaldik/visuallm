<script lang="ts" scoped>
import { defineComponent } from 'vue';
import { PollUntilSuccessGET, PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib';
import type { ProcessedContext } from '@/assets/formatter'
import type { CreateComponentPublicInstance } from 'vue';
import DisplayPlainTextComponent from '@/components/DisplayPlainTextComponent.vue'
import DisplaySoftmaxComponent from '@/components/DisplaySoftmaxComponent.vue'
import DisplaySampleSelectorComponent from '@/components/DisplaySampleSelector.vue'

export default defineComponent({
  data() {
    return {
      picked: "",
      initialContext: {} as ProcessedContext,
      generatedContext: {} as ProcessedContext,
      continuations: {} as ProcessedContext,
      sampleSelector: {} as ProcessedContext,
      tryPoll: undefined as PollUntilSuccessGET | undefined,
      selectPoll: undefined as PollUntilSuccessPOST | undefined,
      samplePoll: undefined as PollUntilSuccessPOST | undefined,
    };
  },
  inject: ['backendAddress'],
  async created() {
    this.tryPoll = new PollUntilSuccessGET(
      `${this.backendAddress}/fetch_next_token_prediction`,
      this.setUpContext.bind(this),
      1000
    )
    await this.tryPoll.newRequest()
  },
  unmounted() {
    this.tryPoll?.clear()
    this.selectPoll?.clear()
  },
  components: {
    DisplayPlainTextComponent,
    DisplaySoftmaxComponent,
    DisplaySampleSelectorComponent,
  },
  methods: {
    setContexts(contexts: [string, any][]) {
      for (let i = 0; i < contexts.length; i++) {
        let name = contexts[i][0] as string
        this[name as keyof CreateComponentPublicInstance] = this.$formatter.processResponseContext(
          contexts[i][1]
        )
      }
    },
    setUpContext(response: any) {
      let contexts = [
        ["sampleSelector", response.sample_selector]
      ] as [string, any][]
      this.setContexts(contexts)
      this.resetDatasetSample(response)
    },
    updateContexts(response: any) {
      let contexts = [
        ["generatedContext", response.generated_context],
        ["continuations", response.continuations]
      ] as [string, any][]
      this.setContexts(contexts)
    },
    resetDatasetSample(response: any) {
      let contexts = [
        ["initialContext", response.initial_context],
      ] as [string, any][]
      this.setContexts(contexts)
      this.updateContexts(response)
    },
    async selectNextToken(picked: string) {
      PollUntilSuccessPOST.startPoll(
        this,
        "selectPoll",
        `${this.backendAddress}/select_next_token_prediction`,
        this.updateContexts.bind(this),
        { token: picked }
      )
    },
    async selectDatasetSample(sample_n: number) {
      PollUntilSuccessPOST.startPoll(
        this,
        "samplePoll",
        `${this.backendAddress}/select_dataset_sample_next_token_prediction`,
        this.resetDatasetSample.bind(this),
        { sample_n: sample_n }
      )
    }
  },
});
</script>

<template>
<div class="horizontal rounded">
  <h2>Next Token Prediction</h2>
  <component :is="sampleSelector.component" :passed_data="sampleSelector.data" @select-number="(sample_n: number) => selectDatasetSample(sample_n)"></component>
  <component :is="initialContext.component" :passed_data="initialContext.data"></component>
  <h3>Generated Context: </h3>
  <component :is="generatedContext.component" :passed_data="generatedContext.data"></component>
  <h3>Possible continuations: </h3>
  <component :is="continuations.component" :passed_data="continuations.data" @picked-softmax="(picked: string) => selectNextToken(picked)"></component>
</div>
</template>
