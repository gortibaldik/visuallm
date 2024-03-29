<template>
    <div :class="{'hmr-wrapper': true, wrapElement: true, vertical: !isHorizontal}">
        <div v-if="text.length > 0" class="descr">{{ text }}</div>
        <div class="input-radio" v-for="choice in choices">
            <input type="radio" v-model="selected" :value="choice"/>
            {{ choice }}
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
import { valuesRequiredInConfiguration } from '@/assets/elementRegistry'
import { dataSharedInComponent, getSharedDataUniqueName, assignRequiredValuesToSharedData } from '@/assets/reactiveData'

let component = defineComponent({
    props: {
        name: {
        type: String,
        required: true
        }
    },
    data() {
        return {
            selected: ""
        }
    },
    computed: {
        choices(): string[] {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'choices')]
        },
        defaultSelected(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'defaultSelected')]
        },
        text(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'text')]
        },
        isHorizontal(): boolean {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'isHorizontal')]
        },
        randomNumber(): number {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'randomNumber')]
        }
    },
    watch: {
        selected: {
            handler(newValue: string) {
                dataSharedInComponent[getSharedDataUniqueName(this.name, 'selected')] = newValue
            },
            immediate: true
        },
        // hack section: thanks to `randomNumber` even if `defaultSelected` is kept the same
        // it will still be reflected in `selected`. The backend sends new `randomNumber` on
        // each request, which is a way to notify the component of a new value arrived from the
        // backend.
        randomNumber: {
            handler(newValue: number) {
                this.selected = this.defaultSelected
            },
            immediate: true
        }
    },
})

export default component

let subtype = 'multi-radio'
export { subtype }

export function processSubElementConfiguration(this_name: string, subElementConfiguration: any) {
    let requiredValues = { choices: 'choices', selected: 'defaultSelected', text: 'text', is_horizontal: "isHorizontal", random_number: "randomNumber"} as {[key: string] : string}
    valuesRequiredInConfiguration(subElementConfiguration, Object.keys(requiredValues))
    return assignRequiredValuesToSharedData(this_name, subElementConfiguration, requiredValues)
}
</script>
<style scoped>
.hmr-wrapper {
    display: flex;
    flex-wrap: wrap;
    column-gap: 5px;
    row-gap: 10px;
}

.vertical {
    flex-direction: column;
    flex-wrap: nowrap;
}

.input-radio {
    box-shadow: rgba(0, 0, 0, 0.16) 0px 10px 36px 0px, rgba(0, 0, 0, 0.06) 0px 0px 0px 1px;
    padding: 5px;
    border: solid;
    border-width: 1px;
    border-color: rgba(0, 0, 0, 0.062);
    border-radius: 3px;
}

.descr {
    padding: 5px;
}
</style>
