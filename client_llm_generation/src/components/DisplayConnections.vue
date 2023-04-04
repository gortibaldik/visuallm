<script lang="ts" scoped>
import { defineComponent } from 'vue';
import TableWithConnectionsComponentVue from './TableWithConnectionsComponent.vue';
import type { LoadedTable, Connection } from './TableWithConnectionsComponent.vue';

export default defineComponent({
    data() {
        return {
            loadedTables: [] as LoadedTable[],
            connections: [] as Connection[],
            pollingInterval: 1,
            howOftenToPollMs: 1000,
            backendAddress: "",
        };
    },
    methods: {
        startPollingServer() {
            this.pollingInterval = setInterval(this.pollBackend.bind(this), this.howOftenToPollMs);
        },
        async pollBackend() {
            let response;
            try {
                response = await fetch(`${this.backendAddress}/fetch_connections`, {
                    method: "GET",
                    headers: {
                        "Accept": "application/json",
                    }
                }).then(response => response.json());
                if (response.result == "success") {
                    clearInterval(this.pollingInterval);
                    this.loadedTables = response.context;
                    this.connections = response.connections;
                }
            }
            catch (err) {
                console.log("Some error - poll backend");
                return;
            }
        },
    },
    created() {
        this.backendAddress = import.meta.env.VITE_API_URL;
        this.startPollingServer();
    },
    unmounted() {
        clearInterval(this.pollingInterval);
    },
    components: { TableWithConnectionsComponentVue }
})
</script>

<template>
  <div>
    <h2>Relations Between Elements</h2>
    <TableWithConnectionsComponentVue :tables="loadedTables" :connections="connections" />
  </div>
</template>