<template>
<span v-if="heading">
    <h1 v-if="headingLevel === 1">{{ value }}</h1>
    <h2 v-else-if="headingLevel === 2">{{ value }}</h2>
    <h3 v-else-if="headingLevel === 3">{{ value }}</h3>
    <h4 v-else-if="headingLevel === 4">{{ value }}</h4>
    <h5 v-else-if="headingLevel === 5">{{ value }}</h5>
    <h6 v-else-if="headingLevel === 6">{{ value }}</h6>
</span>
<div v-else>{{ value }}</div>
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue';
import { reactiveStore } from '@/assets/reactiveData';
import { convertName } from '@/assets/formatter'

class Data {
    value: string
    heading: boolean
    headingLevel: number
    constructor(value: string, heading: boolean, headingLevel: number) {
        this.value = value
        this.heading = heading
        this.headingLevel = headingLevel
    }
}

let component = defineComponent({
    props: {
        name: {
            type: String,
            required: true,
        }
    },
    computed: {
        headingLevel(): number {
            return reactiveStore[convertName(this.name, "headingLevel")]
        },
        heading(): boolean {
            return reactiveStore[convertName(this.name, "heading")]
        },
        value(): string {
            return reactiveStore[convertName(this.name, "value")]
        }
    },
    data() {
        return {
            reactiveStore
        }
    },
})

export default component
export function registerComponent(formatter: any) {
    formatter.registeredComponents["plain"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
    if (! ("content" in context)) {
        throw RangeError("Invalid context ('content' not in context)")
    }
    for (let val of ["value", "heading", "heading_level"]) {
        if (!(val in context.content)) {
            throw RangeError(`Invalid context.content! (without ${val})`)
        }
    }
    return new Data(
        context.content.value,
        context.content.heading,
        context.content.heading_level
    )
}

</script>