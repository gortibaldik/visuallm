# When Does the Library's User Code Execute ?

## Load the page

During the loading only the `ComponentBase.fetch_info()` executes, nothing else.

![Loading of the page](../../readme_images/backend_frontend.png)

### `fetch_info()`

During `fetch_info()` call, all the elements registered into the component are queried with `element.construct_element_description()` call. This call ensures that the element's `changed` property is set to `False` (the `changed` property is set to `True` only when its value changes either by internal means when request comes to change it (e.g. in `ButtonElement`) or by external means when you change its value during some callback), and calls `element.construct_element_configuration()` which constructs the configuration from which the library's frontend implementation reconstructs the element.

The main parts of the `element_description` are these:

- `name`: unique name of the element which is used to identify the element within the component
- `type`: a name which serves to identify what frontend implementation of the element to use
- `address`: elements with endpoints (i.e. elements which inherit from `ElementWithEndpoint`) also include this part based on which the frontend knows which backend API method to call

## Interact with the page

As of now, only static synchronous interactions are supported, i.e. during the call a part of the page reloads and user needs to wait until the callback executes to be able to send any other callback. There exist 3 elements which allow interaction, each time it is in the form of a button: `BarChartElement`, `ButtonElement`, `TextInputElement`.

User clicks on a button
