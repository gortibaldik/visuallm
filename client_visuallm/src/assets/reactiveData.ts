import { reactive } from 'vue'

/** Shared data store for all the elements registered in the component.
 * It allows all the elements on the same level to access data of each
 * other.
 *
 *
 * It is designed in this way so that e.g. a button element could send
 * a request to BE and based on the response update other sibling elements.
 */
export const dataSharedInComponent = reactive({} as { [name: string]: any })

/** Create a key string for a config value for a specific element
 *
 * @param elementName unique name of the element (unique in the context of
 * component)
 * @param configName unique name of the config value (unique in the context
 *  of element)
 * @returns key for a config value within element
 */
export function getSharedDataUniqueName(elementName: string, configName: string): string {
  return `${elementName}>>${configName}`
}

export function getSharedDataElementName(name: string) {
  return name.split('>>')[1]
}

export function assignRequiredValuesToSharedData(
  this_name: string,
  subElementConfiguration: { [key: string]: any },
  requiredValues: { [key: string]: string }
) {
  const data = {} as { [key: string]: any }
  for (const key of Object.keys(requiredValues)) {
    const subElementKey = requiredValues[key]
    data[getSharedDataUniqueName(this_name, subElementKey)] = subElementConfiguration[key]
  }

  return data
}
