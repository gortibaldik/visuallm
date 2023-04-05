<script lang="ts" scoped>
import { defineComponent } from 'vue';
import TableWithConnectionsComponentVue from './TableWithConnectionsComponent.vue';
import type { LoadedTable, Connection } from './TableWithConnectionsComponent.vue';
import { PollUntilSuccessGET } from '@/assets/pollUntilSuccessLib';

export default defineComponent({
    data() {
        return {
            loadedTables: [] as LoadedTable[],
            connections: [] as Connection[],
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
    components: { TableWithConnectionsComponentVue },
    methods: {
        setUpTables(response: any) {
            this.loadedTables = response.context;
            this.connections = response.connections
        },
    },
})
</script>

<template>
  <div>
    <h2>Relations Between Elements</h2>
    <TableWithConnectionsComponentVue :tables="loadedTables" :connections="connections" />
  </div>
</template>