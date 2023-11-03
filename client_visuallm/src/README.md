# Bootstraping - Component Level (3.11.2023)

The user navigates the page, the page creates the list of components which are displayed in the navbar. Afterwards the default component (or the currently navigated component) is loaded.

The component sends a `GET` request to its API endpoint. From this endpoint a message similar to this one arrives:

```json
{
    'elementDescriptions': [
        {'heading': True,
        'heading_level': 2,
        'name': 'plain_text',
        'type': 'plain',
        'value': 'Interactive Generation'},
        ...
        {'address': 'button',
        'button_text': 'Send Dataset Configuration',
        'disabled': False,
        'name': 'button',
        'subelement_configs': [SubElementConfiguration(subtype='choices',
                                                        name='choices',
                                                        configuration={'choices': ['train',
                                                                                'validation'],
                                                                    'selected': 'train',
                                                                    'text': 'Select '
                                                                            'Dataset '
                                                                            'Split'},
                                                        parent_name='button'),
                                SubElementConfiguration(subtype='min_max',
                                                        name='min_max',
                                                        configuration={'max': 131437,
                                                                    'min': 0,
                                                                    'selected': 0,
                                                                    'step_size': 1.0,
                                                                    'text': 'Select '
                                                                            'Dataset '
                                                                            'Sample'},
                                                        parent_name='button')],
        'type': 'button'},
        {'address': 'barchart',
        'long_contexts': True,
        'name': 'barchart',
        'piece_infos': [PieceInfo(pieceTitle='You must be '
                                            'very fast. '
                                            'Hunting is one '
                                            'of my favorite '
                                            'hobbies.',
                                barHeights=[100.0, 100],
                                barAnnotations=['100.00%',
                                                '2.81954'],
                                barNames=['F1-Score',
                                            'Perplexity'])],
        'selectable': False,
        'type': 'softmax'},
        ...
    ],
    'result': 'success'}
```

From this message the component retrieves the names of all the elements which constitute the page. This action happens at the moment when the component is loaded, therefore it is not
possible to change the displayed elements as a response to some API call. (elements inside can be changed, their order and occurrences cannot).

## Processing of the Message

The following call populates `this.elements` list which controls the list of elements that are displayed on the page.

```typescript
this.$elementRegistry.retrieveElementsFromResponse(response, sharedData, this.elements)
```

Each element's configuration is represented by a dictionary which is processed by a `processElementDescr` method which is defined inside each element. For `PlainText`, `Tables`, and `BarChartSelect` element is it a simple mapping, which takes each value from the response and renames it to the value to be consumed by the frontend.

```typescript
let mappingFrontendBackend: { [key: string]: string } = {
  value: 'value',
  heading: 'heading',
  heading_level: 'headingLevel'
}

/**
 *
 * @param elementDescr
 * @param mappingFrontendBackend  an object where key is the name of the config
 *  on the backend side and value is the name of the config on the
 *  frontend side.
 * @returns object that is parsed by ElementRegistry to shared component data
 */
export function processElementDescrBase(
  elementDescr: { [key: string]: any },
  mappingFrontendBackend: { [key: string]: string }
) {
  valuesRequiredInConfiguration(elementDescr, Object.keys(mappingFrontendBackend))
  let returnObject: { [key: string]: any } = {}
  for (const key of Object.keys(mappingFrontendBackend)) {
    returnObject[mappingFrontendBackend[key]] = elementDescr[key]
  }
  return returnObject
}
```

Each key in the returned object is afterwards renamed:

```typescript
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

for (const [key, data] of entries(elementData.data)) {
  reactiveStore[getSharedDataUniqueName(elementDescr.name, key)] = data
}
```

The values in the `reactiveStore` are then used in each of the elements through `computed` properties.
