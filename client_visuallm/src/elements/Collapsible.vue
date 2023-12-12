<template>
    <!-- TODO: better styling of the button -->
    <button :class="{ collapsible: true, active: isOpened, wrapElement: true }" @click="clickedCollapsible">{{ title
    }}</button>
    <div class="subcomponent content" ref="content" v-if="isOpened">
        <!-- TODO: look at this https://vuejs.org/guide/components/events.html -->
        <component v-for="(element, idx) in elements" :key="idx" :is="element.component" :name="element.name" @make-bigger="onMakeBigger" @make-smaller="onMakeSmaller"/>
    </div>
</template>

<script lang="ts" scoped>
import ElementRegistry, { registerElementBase, type ProcessedContext } from '@/assets/elementRegistry';
import { dataSharedInComponent, getSharedDataUniqueName } from '@/assets/reactiveData';
import { defineComponent} from 'vue';
import PlainText from '@/elements/PlainText.vue'
import BarChartSelect from '@/elements/BarChartSelect.vue'
import Selector from '@/elements/Selector.vue'
import Tables from '@/elements/Tables.vue'

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
            heights: {} as {[key: string]: number},
            resizeTimeout: -1 as number,
            runAfterTimeout: function() {}
        }
    },
    created() {
        if (!this.isCollapsed) {
            this.clickedCollapsible()
        }
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
                let obj = {
                    component: this.$elementRegistry.registeredElements[this.elemDescrs[i].type].component,
                    name: elements[i].name
                }
                reactiveElements.push(obj)
            }
            setTimeout(() => this.resizeContent(this.isOpened), 100)
            return reactiveElements
        },
        title(): string {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, 'title')]
        },
        isCollapsed(): boolean {
            return dataSharedInComponent[getSharedDataUniqueName(this.name, "isCollapsed")]
        }
    },
    methods: {
        /** Return all the values of the dict
         */
        dictValues(dict: {[key: string]: number}) {
            return Object.keys(dict).map(function(key){
                return dict[key];
            });
        },
        onMakeBigger(requiredTotalHeight: number, idOfCaller: string) {
            // if we are currently in the process of making the collapsible smaller,
            // just wait for the process to end and then run the method "runAfterTimeout"
            if (this.resizeTimeout > 0) {
                this.runAfterTimeout = () => this.onMakeBigger(requiredTotalHeight, idOfCaller)
                return
            }

            let content = this.$refs.content as HTMLElement
            let clientRect = content.getBoundingClientRect()
            let newHeightNumber = requiredTotalHeight - clientRect.y

            // if the collapsible is already big enough, do not do anything
            if (newHeightNumber < Math.max(...this.dictValues(this.heights))) {
                this.heights[idOfCaller] = newHeightNumber
                return
            }
            this.heights[idOfCaller] = newHeightNumber
            let newHeight = newHeightNumber + "px"
            content.style.height = newHeight
            content.style.maxHeight = newHeight
        },
        onMakeSmaller(idOfCaller: string) {
            let content = this.$refs.content as HTMLElement

            delete this.heights[idOfCaller]

            // become a level smaller
            let newHeightNumber = Math.max(...this.dictValues(this.heights))
            let newHeight = newHeightNumber + "px"
            this.resizeTimeout = setTimeout(this.resizeToNewHeight.bind(this, newHeight), 200)
            content.style.maxHeight = newHeight
        },
        resizeToNewHeight(newHeight: string) {
            let content = this.$refs.content as HTMLElement
            content.style.height = newHeight
            this.resizeTimeout = -1
            this.runAfterTimeout()
            this.runAfterTimeout = function() {}
        },
        resizeContent(shouldOpen: boolean) {
            let content = this.$refs.content as HTMLElement
            if (!shouldOpen) {
                this.heights = {}
                // @ts-ignore
                content.style.maxHeight = null
                return
            }
            this.heights["default"] = content.scrollHeight
            content.style.maxHeight = content.scrollHeight + "px"
        },
        clickedCollapsible() {
            if (!this.isOpened) {
                this.isOpened = true
                this.$nextTick(this.resizeContent.bind(this, true))
            } else {
                this.resizeContent(false)
                setTimeout(() => this.isOpened = false, 200)
            }

        }
    }
})

let FEBEMapping: { [key: string]: string } = {
    "subelements": "subelements",
    "title": "title",
    "is_collapsed": "isCollapsed",
}

export function registerElement(elementRegistry: ElementRegistry) {
    registerElementBase(elementRegistry, "collapsible-element", "Collapsible", FEBEMapping)
}

export default component
</script>

<style scoped>
.content {
    /* padding: 0 18px; */
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.2s ease-out;
    background-color: rgb(246, 244, 244);
    border-bottom: 0.2px solid grey;
    border-left: 0.2px solid grey;
    border-right: 0.2px solid grey;
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
    width: 100%;
    margin-left: 0;
    margin-right: 0;
    border: none;
    text-align: center;
    /* outline: none; */
    /* font-size: 15px; */
}
</style>
