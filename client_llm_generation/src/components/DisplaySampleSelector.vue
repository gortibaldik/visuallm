<template>
    <div class="sample-selector">
        Select dataset sample to display: 
        <input type="number" :min="passed_data.min" :max="passed_data.max" v-model="sample_n"/>
        <button class="button emit" @click="emitClicked()">Select</button>
    </div>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue'
interface DataParams {
    min: number,
    max: number
}

class Data {
    min: number
    max: number
    constructor({ min, max }: DataParams) {
        this.min = min
        this.max = max
    }
}

let component = defineComponent({
    props: {
        passed_data: {
            type: Data,
            required: true
        }
    },
    computed: {
    },
    emits: ["select-number"],
    data() {
        return {
            sample_n: this.middleRange() as number,
        }
    },
    watch: {
        sample_n(new_value: number) {
            this.sample_n = Math.max(
                Math.min(
                    Math.round(new_value),
                    this.passed_data.max
                ),
                this.passed_data.min
            )
        }
    },
    methods: {
        emitClicked() {
            this.$emit("select-number", this.sample_n)
        },
        middleRange(): number {
            let min = this.passed_data.min
            let max = this.passed_data.max
            return Math.floor(min + (max - min) / 2)
        }
    }
})

export default component
export function registerComponent(formatter: any) {
    formatter.registeredComponents["sample_selector"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
    return new Data({
        min: context.content.min,
        max: context.content.max
    })
}
</script>

<style scoped>
.sample-selector {
    font-family: sans-serif;
    font-weight: normal;
}

.button {
    display: inline-block;
    padding: 5px;
    padding-left: 10px;
    padding-right: 10px;
    margin-left: 5px;
}

</style>