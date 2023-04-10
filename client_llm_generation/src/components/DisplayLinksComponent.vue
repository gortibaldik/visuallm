<template>
<div v-for="table in passed_data.loadedTables" class="table-wrapper">
    <h3 v-if="table.title != undefined">{{ table.title }}</h3>
    <table class="table-style-0">
        <thead><tr>
            <th v-for="val in table.headers">{{ val }}</th>
        </tr></thead>
        <tbody>
            <tr v-for="(row, r) in table.rows" :id="`${table_title_to_id(table.title)}_${r}`" :class="{ active: shownName == `${table_title_to_id(table.title)}_${r}`}">
                <td v-for="col in row">{{ col }}</td>
            </tr>
        </tbody>
    </table>
</div>
</template>

<script lang="ts" scoped>
import { defineComponent } from 'vue';
import LeaderLine from 'leader-line-new';
import { shallowRef } from 'vue';

export type LoadedTable = {
    title: string,
    headers: string[],
    rows: string[][]
}

export type Connection = {
    StartTable: string;
    StartId: number;
    EndTable: string;
    EndId: number;
    Importance: number;
    Label: string;
}

class Data {
    loadedTables: LoadedTable[]
    connections: Connection[]
    constructor(loadedTables: LoadedTable[], connections: Connection[]) {
        this.loadedTables = loadedTables
        this.connections = connections
    }
}

let component = defineComponent({
    props: {
        passed_data: {
            type: Data,
            required: true
        }
    },
    data() {
        return {
            connections: this.passed_data.connections,
            tables: this.passed_data.loadedTables,
            tableRefs: {} as { [id: string] : number },
            initializeConnectionsTimeoutMS: 400,
            shownConnections: {} as { [id: string]: boolean;},
            shownName: undefined as string | undefined,
            drawedConnections: {} as { [id: string]: LeaderLine[]}
        }
    },
    mounted() {
        this.initializeTableRefs(this.tables)
        setTimeout(this.initializeConnections.bind(this), 500)
    },
    unmounted() {
        for (let key in this.drawedConnections) {
            let lines = this.drawedConnections[key];
            for (let i = 0; i < lines.length; i++) {
                let line = lines[i];
                line.remove();
            }
        }
    },
    watch: {
        passed_data(newValue: any) {
            console.log("tables changed!")
            this.initializeTableRefs(this.tables)
            setTimeout(this.initializeConnections.bind(this), 500)
        }
    },
    methods: {
        table_title_to_id(title: string) {
            return title.replace(/\s/g, '')
        },
        initializeTableRefs(newTables: LoadedTable[]) {
            this.tableRefs = {}
            for (let i = 0; i < newTables.length; i++) {
                this.tableRefs[newTables[i].title] = i
            }
        },
        removeConnections() {
            console.log("removing connections!")
            for (let key in this.drawedConnections) {
                let lines = this.drawedConnections[key];
                for (let i = 0; i < lines.length; i++) {
                    let line = lines[i];
                    line.remove();
                }
            }
            this.drawedConnections = {}
        },
        initializeConnections() {
            let connections = this.passed_data.connections
            if (connections == undefined) {
                return
            }
            this.removeConnections()
            for (let i = 0; i < connections.length; i++) {
                let connection = connections[i] as Connection

                let startName = `${this.table_title_to_id(connection.StartTable)}_${connection.StartId}`
                let endName = `${this.table_title_to_id(connection.EndTable)}_${connection.EndId}`

                let elStart = document.getElementById(startName)
                let elEnd = document.getElementById(endName)
                
                if ((elStart != null) && (elEnd != null)) {
                    const myLine = new LeaderLine(elStart, elEnd, {
                        startSocket: "right",
                        endSocket: "right",
                        path: "grid",
                        size: connection.Importance,
                        startSocketGravity: [150, 0],
                        startPlug: "square",
                        endPlugSize: 4 / connection.Importance,
                        endLabel: LeaderLine.captionLabel(connection.Label, { offset: [25, -25] }),
                        hide: true,
                    });
                    if (!(startName in this.drawedConnections)) {
                        this.drawedConnections[startName] = [];
                        this.shownConnections[startName] = false;
                        elStart?.addEventListener("mouseover", this.showRowConnections.bind(this, startName));
                    }
                    this.drawedConnections[startName].push(myLine);
                }
            }
        },
        showRowConnections(rowID: string) {
            if (!this.shownConnections[rowID]) {
                let connections = this.drawedConnections[rowID];
                for (let i = 0; i < connections.length; i++) {
                    connections[i].show("draw", { duration: 500 });
                }
                if (this.shownName != undefined) {
                    let connections = this.drawedConnections[this.shownName];
                    for (let i = 0; i < connections.length; i++) {
                        connections[i].hide("none");
                    }
                    this.shownConnections[this.shownName] = false;
                }
                this.shownName = rowID;
                this.shownConnections[rowID] = true;
            }
        },
    },
})

export default component
export function registerComponent(formatter: any) {
    formatter.registeredComponents["connected_tables"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
    return new Data(
        context.content.tables,
        context.content.connections
    )
}
</script>

<style scoped>
.table-wrapper h3 {
  text-align: center;
  margin-top: 0px;
}

.table-wrapper {
    width: fit-content;
    margin-top: 10px;
    background-color: rgba(0, 0, 0, 0.127);
    border-style:dashed;
    border-width: 1px;
    padding: 5px;
    border-radius: 5px;
    box-shadow: 0px 35px 50px rgba( 0, 0, 0, 0.2) ;
}
.table-style-0 {
    border-radius: 5px;
    font-size: 12px;
    font-weight: normal;
    border: none;
    border-collapse: collapse;
    max-width: 100%;
    white-space: nowrap;
    background-color: white;
}
.table-style-0 td, .table-style-0 th {
    text-align: left;
    padding: 8px;
}

.table-style-0 td {
    border-right: 1px solid #f8f8f8;
    font-size: 12px;
}

.table-style-0 thead th {
    color: #ffffff;
    background: #7c7c7c;
    padding-right: 10px;
    padding-left: 10px;
}


.table-style-0 thead th:nth-child(odd) {
    color: #ffffff;
    background: #6d6d6d;
    padding-right: 10px;
    padding-left: 10px;
}

.table-style-0 tr:nth-child(even) {
    background: #efeeee;
    padding-right: 10px;
    padding-left: 10px;
}

.table-style-0 .active {
    background: #fbd0d0 !important;
}

</style>