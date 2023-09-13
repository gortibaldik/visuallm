import type { App } from 'vue'
import { PollUntilSuccessGET } from './pollUntilSuccessLib'

interface Instance {
  $router: any
  $default_fetch_paths: { [name: string]: string },
  [pollName: string]: any,
}

/** Fetch the information about all the elements at the start of the component lifecycle.
 *
 * @param instance the component that holds '$router', 'backendAddress' and '$default_fetch_paths'
 * @param pollName the name that the poll should get
 * @param callback function that should be called after the poll succeeds and the function gets repsponse from the backend
 */
export async function fetchDefault(
  instance: Instance,
  backendAddress: string,
  pollName: string,
  callback: (response: any) => void
) {
  const route_name = instance['$router'].currentRoute.value.name
  if (route_name === undefined || route_name === null) {
    throw TypeError()
  }
  const name = route_name.toString() as string
  const default_fetch_path = instance['$default_fetch_paths'][name] as string
  instance[pollName]?.clear()
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
