import type { Component, App } from 'vue';

export type ProcessedContext = {
    component: Component,
    data: Map<string, any>
}

export default class Formatter {
    registeredComponents: { [id: string]: { [name: string] : any}}

    constructor() {
        this.registeredComponents = {}
    }

    processResponseContext(context: any): {component: Component, data: Map<string, any>} {
        if (context === undefined) {
            throw RangeError("Context is undefined!")
        }
        if (! (context.type in this.registeredComponents)) {
            throw RangeError(`context.type: "${context.type}" isn't registered in formatter!`)
        }
        let componentDict = this.registeredComponents[context.type]
        let resultDict = {
            component: componentDict.component,
            data: componentDict.process(context)
        }
        return resultDict
    } 

    install(app: App) {
        app.config.globalProperties.$formatter = this
    }
}
