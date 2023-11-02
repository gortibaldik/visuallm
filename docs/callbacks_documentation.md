# When Does the Library's User Code Execute ?

## Load the page

During the loading only the `ComponentBase.fetch_info()` executes, nothing else.

![Loading of the page](../readme_images/backend_frontend.png)

### `fetch_info()`

During `fetch_info()` call, all the elements registered into the component are queried with `element.construct_element_description()` call. This call ensures that the element's `changed` property is set to `False` (the `changed` property is set to `True` only when its value changes either by internal means when request comes to change it (e.g. in `ButtonElement`) or by external means when you change its value during some callback), and calls `element.construct_element_configuration()` which constructs the configuration from which the library's frontend implementation reconstructs the element.

The main parts of the `element_description` are these:

- `name`: unique name of the element which is used to identify the element within the component
- `type`: a name which serves to identify what frontend implementation of the element to use
- `address`: elements with endpoints (i.e. elements which inherit from `ElementWithEndpoint`) also include this part based on which the frontend knows which backend API method to call

## Interact with the page

As of now, only static synchronous interactions are supported, i.e. during the call a part of the page reloads and user needs to wait until the callback executes to be able to send any other callback. There exist 3 elements which allow interaction, each time it is in the form of a button: `BarChartElement`, `ButtonElement`, `TextInputElement`.

User clicks on a button. The frontend sends a message with all the information from the element to the backend. The elements `endpoint_callback()` function handles the response.

The flow is the same for all the elements. At first the values from the message from the frontend are extracted to element _E_ properties. If any property has been updated with a new value the _E_'s `changed` property is set to `True`. Then the `E.processing_callback()` is called.

`processing_callback()` is a function in which the library's user can handle the change of any important value. Let's look at an example from [`ModelSelectionMixin`](../visuallm/components/mixins/model_selection_mixin.py). This mixin allows the user to select from an array of models. In order to do this there is a `ButtonElement` with `ChoicesSubElement`. When the user clicks on the button, the choice selected in `ChoicesSubElement` is sent to the backend. There the `ModelSelectionMixin` inspects whether `ChoicesSubElement.changed` property is set to `True` and if so, the `ModelSelectionMixin` loads a new model, otherwise it ignores the message.
