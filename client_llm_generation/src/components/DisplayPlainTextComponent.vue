<template>
{{ passed_data.value }}
</template>

<script lang="ts">
import { defineComponent, shallowRef } from 'vue';

class Data {
    value: string
    constructor(value: string) {
        this.value = value
    }
}

let component = defineComponent({
    props: {
        passed_data: {
            type: Data,
            required: true
        }
    }
})

export default component
export function registerComponent(formatter: any) {
    formatter.registeredComponents["plain"] = {
        component: shallowRef(component),
        process: processContext
    }
}

function processContext(context: any) {
    return new Data(context.content)
}

</script>