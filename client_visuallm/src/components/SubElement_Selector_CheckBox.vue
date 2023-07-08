<template>
    <div :class="{ wrapElement: true, focused: isFocused }">
        <span class="checkbox-text">{{ text }}</span>
        <input type="checkbox" v-model="selected" @focus="isFocused = true" @blur="isFocused = false" />
    </div>
</template>

<script lang="ts">
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry';
import { componentSharedData, getSharedDataUniqueName, assignRequiredValuesToSharedData } from '@/assets/reactiveData';
import { defineComponent } from 'vue'

let component = defineComponent({
    props: {
        name: {
            type: String,
            required: true
        }
    },
    computed: {
        text(): string {
            return componentSharedData[getSharedDataUniqueName(this.name, 'text')]
        },
        defaultSelected(): boolean {
            return componentSharedData[getSharedDataUniqueName(this.name, 'defaultSelected')]
        },
    },
    data() {
        return {
            selected: false as boolean,
            isFocused: false as boolean,
        }
    },
    watch: {
        selected: {
            handler(new_value: boolean) {
                let nameSelected = getSharedDataUniqueName(this.name, "selected")
                componentSharedData[nameSelected] = new_value
            },
            immediate: true
        },
        defaultSelected: {
            handler(newValue: boolean) {
                this.selected = newValue
            },
            immediate: true
        }
    }
})
export default component

let subtype = 'check_box'
export { subtype }

export function processSubElementConfiguration(this_name: string, subElementConfiguration: any) {
    let requiredValues = { text: 'text', selected: 'defaultSelected' } as { [key: string]: string }
    valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))

    let data = assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
    return data
}
</script>
<style scoped>
.checkbox-text {
    margin-right: 5px;
}
</style>
