<template>
    <div class="sample-selector">
        Select dataset sample to display: 
        <input type="number" :min="min" :max="max" v-model="sample_n"/>
        <button class="button emit" @click="emitClicked()">Select</button>
    </div>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue'
import { reactiveStore } from '@/assets/reactiveData'
import { convertName } from '@/assets/formatter'
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib'

interface DataParams {
    min: number,
    max: number,
    callbackAddress: string,
}

class Data {
    min: number
    max: number
    callbackAddress: string
    constructor({ min, max, callbackAddress }: DataParams) {
        this.min = min
        this.max = max,
        this.callbackAddress = callbackAddress
    }
}

let component = defineComponent({
    props: {
        name: {
            type: String,
            required: true
        }
    },
    computed: {
        max(): number {
            return reactiveStore[convertName(this.name, "max")]
        },
        min(): number {
            return reactiveStore[convertName(this.name, "min")]
        },
        callbackAddress(): string {
            return reactiveStore[convertName(this.name, "callbackAddress")]
        }
    },
    inject: [ "backendAddress" ],
    data() {
        return {
            sample_n: 0 as number,
            reactiveStore,
            selectSamplePoll: undefined as undefined | PollUntilSuccessPOST
        }
    },
    watch: {
        sample_n(new_value: number) {
            this.sample_n = Math.max(
                Math.min(
                    Math.round(new_value),
                    this.max
                ),
                this.min
            )
        }
    },
    mounted() {
        this.sample_n = this.middleRange()
    },
    unmounted() {
        this.selectSamplePoll?.clear()
    },
    methods: {
        emitClicked() {
            PollUntilSuccessPOST.startPoll(
                this,
                "selectSamplePoll",
                `${this.backendAddress}/${this.callbackAddress}`,
                this.setContexts.bind(this),
                { sample_n: this.sample_n }
            )
        },
        setContexts(response: any) {
            this.$formatter.processResponse(
                response,
                this.reactiveStore
            )
        },
        middleRange(): number {
            let min = this.min
            let max = this.max
            return Math.floor(min + (max - min) / 2)
        }
    },
})

export default component
export function registerComponent(formatter: any) {
    formatter.registeredComponents["sample_selector"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
    if (! ("content" in context)) {
        throw RangeError("Invalid context ('content' not in context)")
    }
    if (! ("min" in context.content) || ! ("max" in context.content)) {
        throw RangeError("Invalid context.content! (without min or max)")
    }
    if (! ("address" in context.content)) {
        throw RangeError("Invalid context content! (without address)")
    }
    return new Data({
        min: context.content.min,
        max: context.content.max,
        callbackAddress: context.content.address
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