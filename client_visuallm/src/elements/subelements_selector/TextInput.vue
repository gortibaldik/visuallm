<template>
    <textarea :placeholder="placeholderText" v-model="selected" />
</template>

<script lang="ts">
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry';
import { assignRequiredValuesToSharedData, dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData';
import { defineComponent } from 'vue'

let component = defineComponent({
    data() {
        return {
            selected: "" as string,
        }
    },
    props: {
        name: {
            type: String,
            required: true
        }
    },
    computed: {
        buttonText(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'buttonText')]
        },
        placeholderText(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'placeholderText')]
        },
        textInputFromBackend(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'valueFromBackend')]
        },
        blankAfterTextSend(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'blankAfterTextSend')]
        },
        randomNumber(): number {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'randomNumber')]
        }
    },
    watch: {
        textInputFromBackend: {
            handler(newValue: string) {
                this.selected = newValue
            },
            immediate: true
        },
        // hack section: backend sends each time a different random number, so that `this.selected` would
        // be updated even if the this.textInputFromBackend wouldn't change
        randomNumber: {
            handler(newValue: number) {
                if (this.blankAfterTextSend) {
                    this.selected = this.textInputFromBackend
                }
            },
            immediate: true
        },
        selected: {
            handler(newValue: string) {
                let nameSelected = getSharedDataUniqueName(this.name, 'selected')
                dataSharedInComponent[nameSelected] = newValue
            },
            immediate: true
        }
    },
})

export default component

export function processSubElementConfiguration(this_name: string, subElementConfiguration: any) {
    let requiredValues = { placeholder_text: 'placeholderText', selected: 'valueFromBackend', blank_after_text_send: 'blankAfterTextSend', random_number: 'randomNumber' }
    valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))

    let data = assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
    return data
}

let subtype = "text_input"
export { subtype }

</script>
<style scoped>
textarea {
    display: flex;
    flex-basis: 100%;
    font-family: sans-serif;
    font-weight: normal;
    padding-top: 7px;
    padding: 5px;
}
</style>
