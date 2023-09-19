<template>
    <form @submit.prevent="submit" class="wrapElement text-input-wrapper">
        <textarea :placeholder="defaultText" v-model="textInput" @keydown.enter.prevent="" @keyup.enter="submit" />
        <button class="button-override button" type="submit">{{ buttonText }}</button>
    </form>
</template>

<script lang="ts">
import { valuesRequiredInConfiguration, ElementDescription } from '@/assets/elementRegistry';
import type ElementRegistry from '@/assets/elementRegistry';
import { PollUntilSuccessPOST } from '@/assets/pollUntilSuccessLib';
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData';
import { defineComponent, shallowRef } from 'vue'

let component = defineComponent({
    data() {
        return {
            submitTextPoll: undefined as undefined | PollUntilSuccessPOST,
            textInput: "" as string,
        }
    },
    props: {
        name: {
            type: String,
            required: true
        }
    },
    inject: ['backendAddress'],
    computed: {
        buttonText(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'buttonText')]
        },
        defaultText(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'defaultText')]
        },
        address(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'address')]
        },
        textInputFromBackend(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'textInputFromBackend')]
        }
    },
    watch: {
        textInputFromBackend: {
            handler(newValue: string) {
                this.textInput = newValue
            },
            immediate: true
        }
    },
    created() {
        this.textInput = this.textInputFromBackend
    },
    methods: {
        submit() {
            PollUntilSuccessPOST.startPoll(
                this,
                'submitTextPoll',
                `${this.backendAddress}/${this.address}`,
                this.processResponse.bind(this),
                { text_input: this.textInput }
            )
        },
        processResponse(response: any) {
            this.$elementRegistry.retrieveElementsFromResponse(response, dataSharedInComponent)
            this.textInput = this.textInputFromBackend
        }
    }
})

export default component
/**
 *
 * @param elementRegistry this parameter holds all the elements that can be created
 * from the backend
 */
export function registerElement(elementRegistry: ElementRegistry) {
    elementRegistry.registeredElements['text_input'] = {
        component: shallowRef(component),
        process: processElementDescr
    }
}

class ElementConfiguration extends ElementDescription {
    button_text!: string
    default_text!: string
    text_input!: string
    address!: string
}

function processElementDescr(elementDescr: ElementConfiguration) {
    valuesRequiredInConfiguration(elementDescr, ["button_text", "default_text", "address", "text_input"])

    return {
        buttonText: elementDescr.button_text,
        defaultText: elementDescr.default_text,
        address: elementDescr.address,
        textInputFromBackend: elementDescr.text_input
    }
}

</script>
<style scoped>
.text-input-wrapper {
    display: flex;
    flex-direction: row;
    column-gap: 10px;
    align-items: center;
}

button {
    display: flex;
}

.button-override {
    padding: 5px;
    padding-top: 7px;
}

textarea {
    display: flex;
    flex-grow: 2;
    font-family: sans-serif;
    font-weight: normal;
    padding-top: 7px;
    padding: 5px;
}
</style>
