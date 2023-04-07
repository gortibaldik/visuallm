<script lang="ts" scoped>
import { defineComponent } from 'vue';
import DisplayLinksComponent from './DisplayLinksComponent.vue';
import { PollUntilSuccessGET } from '@/assets/pollUntilSuccessLib';
import type { ProcessedContext } from '@/assets/formatter';

export default defineComponent({
    data() {
        return {
            tablesContext: {} as ProcessedContext,
            tryPoll: undefined as undefined | PollUntilSuccessGET
        };
    },
    inject: [ "backendAddress" ],
    created() {
        this.tryPoll = new PollUntilSuccessGET(
            `${this.backendAddress}/fetch_connections`,
            this.setUpTables.bind(this),
        )
        this.tryPoll.newRequest()
    },
    unmounted() {
        this.tryPoll?.clear()
    },
    components: { DisplayLinksComponent },
    methods: {
        setUpTables(response: any) {
            this.tablesContext = this.$formatter.processResponseContext(
                response.content
            )
        },
    },
})
</script>

<template>
  <div>
    <h2>Relations Between Elements</h2>
    <component :is="tablesContext.component" :passed_data="tablesContext.data"></component>
  </div>
</template>