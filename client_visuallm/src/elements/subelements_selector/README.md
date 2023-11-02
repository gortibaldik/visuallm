# Communication between Subelements and Main Selector Element

The selector element is constructed when a message in the following format arrives from the backend:

```json
{
    'address': "<address_where_to_send_api_calls>"
    'button_text': "<button_text>"
​    'disabled': "<is_button_clickable?>"
    'name': "<unique_element_name_in_the_component>"​
    `subelement_configs`: [
        {
            'name': "<unique_subelement_name_in_the_selector_element>"
            'parent_name': "<name_of_parent>"
            'subtype': "<type_of_the_subelement>"
            'configuration': { <dict with all the values needed for the specific subelement> }
        }
    ]
}
```

When this message arrives, the whole selector element is reconstructed.

## Data Sharing between Selector and its Subelements

The frontend uses a shared datastore:

```vuejs
dataSharedInComponent = reactive({} as { [name: string]: any })
```

Each subelement has a unique name in this datastore which is:

```
`selector_name`>>`subelement_name`
```

i.e.

```
button>>text_input
```

and each data-point that needs to be shared between the subelement and the parent selector element is stored in this datastore.

One such crucial data-point is the `selected` value, which contains the user's choice and is sent to the backend. The preferred way to share the `selected` value is the following code snippet:

```js
watch: {
    selected: {
        handler(new_value: string) {
            let nameSelected = getSharedDataUniqueName(this.name, 'selected')
            dataSharedInComponent[nameSelected] = new_value
        },
        immediate: true
    }
}
```

`getSharedDataUniqueName` constructs the name of the `selected` property in the shared component datastore, watcher on each change of the `selected` value changes the value saved in the shared datastore, `immediate` ensures that the first change is saved in the datastore too.

## Sending Data to Backend

The selector sends every subelement's `selected` value to the backend, after receiving the response it sets all the elements' configurations to the shared datastore.

### TextInput specifics

The TextInput subelement is special, because it's a common situation that the `textarea` is erased after sending the value to the backend.

This means that on the backend each time the value from the TextInput subelement arrives we set `subelement.value_from_frontend` to the value that user entered on the frontend, however `subelement.value_on_backend` (the value that will be sent to update the frontend) is set to `""`.

Hence any time the update to the frontend arrives, it has the same value `subelement.value_on_backend===""`. Therefore the TextInput subelement also sents whether the textarea should be blanked after each submit and a random number generated on the backend. Each time the backend processes the response, the number is regenerated, hence the frontend receives a new random number and therefore it can update the `textarea`. (Vue.js works with reactivity, it wouldn't update the textarea if the `subelement.value_on_backend` remained the same.)
