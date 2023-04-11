import type { App } from 'vue'
import { PollUntilSuccessGET } from './pollUntilSuccessLib'

export async function fetchDefault(instance: any, backendAddress: string, pollName: string, callback: any) {
    let route_name = instance["$router"].currentRoute.value.name
    if (route_name === undefined || route_name === null) {
      throw TypeError()
    }
    let name = route_name.toString()
    let default_fetch_path = instance["$default_fetch_paths"][name]
    instance[pollName] = new PollUntilSuccessGET(
      `${backendAddress}/${default_fetch_path}`,
      callback,
      1000
    )
    await instance[pollName].newRequest()
}

export default {
    install(app: App) {
        app.config.globalProperties.$default_fetch_paths = {}
    }
}