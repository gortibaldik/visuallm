<script lang="ts" scoped>
import { defineComponent } from 'vue';
import DisplayLinksComponent from './DisplayLinksComponent.vue';
import { PollUntilSuccessGET, PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib';
import type { ProcessedContext } from '@/assets/formatter';
import { fetchDefault } from '@/assets/fetchPathsResolver';

export default defineComponent({
    data() {
        return {
            tablesContext: {} as ProcessedContext,
            sampleSelector: {} as ProcessedContext,
            defaultPoll: undefined as undefined | PollUntilSuccessGET,
            samplePoll: undefined as undefined | PollUntilSuccessPOST
        };
    },
    inject: [ "backendAddress" ],
    created() {
        fetchDefault(
            this,
            this.backendAddress as string,
            "defaultPoll",
            this.setUpTables.bind(this)
        )
    },
    unmounted() {
        this.defaultPoll?.clear()
    },
    components: { DisplayLinksComponent },
    methods: {
        setUpTables(response: any) {
            this.tablesContext = this.$formatter.processResponseContext(
                response.content
            )
            this.sampleSelector = this.$formatter.processResponseContext(
                response.sample_selector
            )
        },
        async selectDatasetSample(sample_n: number) {
            PollUntilSuccessPOST.startPoll(
                this,
                "samplePoll",
                `${this.backendAddress}/select_dataset_sample_links`,
                this.setUpTables.bind(this),
                { sample_n: sample_n }
            )
        }
    },
})
</script>

<template>
  <div>
    <h2>Relations Between Elements</h2>
    <component :is="sampleSelector.component" :passed_data="sampleSelector.data" @select-number="(sample_n: number) => selectDatasetSample(sample_n)"></component>
    <component :is="tablesContext.component" :passed_data="tablesContext.data"></component>
  </div>
</template>