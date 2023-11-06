<template>
    <!-- TODO: better styling of the button -->
    <button :class="{ collapsible: true, active: isOpened, wrapElement: true }" @click="clickedCollapsible">{{ title
    }}</button>
    <div class="subcomponent content" ref="content" v-if="isOpened">
        <component v-for="(element, idx) in elements" :key="idx" :is="element.component" :name="element.name" />
    </div>
</template>

<script lang="ts" scoped>
import ElementRegistry, { registerElementBase, type ProcessedContext } from '@/assets/elementRegistry';
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData';
import { defineComponent, type Ref } from 'vue';
import PlainText from '@/elements/PlainText.vue'
import BarChartSelect from '@/elements/BarChartSelect.vue'
import Selector from '@/elements/Selector.vue'
import Tables from '@/elements/Tables.vue'
import { reactive } from 'vue';

interface SubComponentElement {
    type: string
    name: string
}

let component = defineComponent({
    props: {
        name: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            isOpened: false,
        }
    },
    created() {
        console.log("collapsible created!")
    },
    components: {
        PlainText,
        BarChartSelect,
        Selector,
        Tables
    },
    computed: {
        elemDescrs(): SubComponentElement[] {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'subelements')] as SubComponentElement[]
        },
        elements(): ProcessedContext[] {
            let subResponse = {
                result: "success",
                reason: undefined,
                elementDescriptions: this.elemDescrs
            }

            let elements = [] as ProcessedContext[]
            this.$elementRegistry.retrieveElementsFromResponse(subResponse, dataSharedInComponent, elements)

            let reactiveElements = [] as ProcessedContext[]
            // if the displayed object isn't marked as reactive, then for some reason
            // it isn't displayed (vue component is not rendered)
            for (let i = 0; i < elements.length; i++) {
                let obj = reactive({
                    component: this.$elementRegistry.registeredElements[this.elemDescrs[i].type].component,
                    name: elements[i].name
                })
                reactiveElements.push(obj)
            }
            return reactiveElements
        },
        title(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'title')]
        }
    },
    methods: {
        resizeContent() {
            let content = this.$refs.content as HTMLElement
            if (!this.isOpened) {
                return
            }
            content.style.maxHeight = content.scrollHeight + "px"
        },
        clickedCollapsible() {
            if (!this.isOpened) {
                this.isOpened = true
                this.$nextTick(this.resizeContent.bind(this))
            } else {
                this.isOpened = false
            }

        }
    }
})

let FEBEMapping: { [key: string]: string } = {
    "subelements": "subelements",
    "title": "title"
}

export function registerElement(elementRegistry: ElementRegistry) {
    registerElementBase(elementRegistry, "collapsible-subcomponent", component, FEBEMapping)
}

export default component
</script>

<style scoped>
.content {
    /* padding: 0 18px; */
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
    background-color: white;
}

.active,
.collapsible:hover {
    background-color: rgba(0, 0, 0, 0.3);
}

.collapsible {
    background-color: rgba(0, 0, 0, 0.409);
    /* color: white; */
    /* cursor: pointer; */
    /* padding: 18px; */
    display: block;
    left: 0;
    right: 0;
    width: calc(100% - 10px);
    border: none;
    text-align: center;
    /* outline: none; */
    /* font-size: 15px; */
}
</style>
