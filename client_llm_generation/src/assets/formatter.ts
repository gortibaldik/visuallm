import type { Component, App } from 'vue';

export type ProcessedContext = {
    component: Component,
    name: string
}

export function convertName(componentName: string, dataName: string):string {
    return `${componentName}>>${dataName}`
}

export function* entries(obj: any) {
    for (let key of Object.keys(obj)) {
      yield [key, obj[key]];
    }
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

    processResponse(response: any, reactiveStore: {[name: string] : any}, contexts: {[name: string]: any} | undefined = undefined) {
        let responseContexts = response.contexts as []
        for (let i = 0; i < responseContexts.length; i++) {
            let context = responseContexts[i] as { name: string, content: any, type: string }
            let name = context.name
            let resultDict = this.processResponseContext(context)
            if (contexts !== undefined) {
                contexts[name] = {
                    component: resultDict.component,
                    name: name
                }
            }
            for (let [key, data] of entries(resultDict.data)) {
                reactiveStore[convertName(name, key)] = data
            }
        }
    }

    install(app: App) {
        app.config.globalProperties.$formatter = this
    }
}
