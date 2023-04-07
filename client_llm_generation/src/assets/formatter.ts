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
