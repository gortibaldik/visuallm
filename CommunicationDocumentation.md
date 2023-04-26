# Documentation of Communication between BE and FE

## Fetch Components Phase

User navigates to `http://localhost:5000`, BE returns initial Vue.js component which handles fetching of the components.

FE calls `http://localhost:5000/fetch_components`, BE returns a list of all components (tabs) from which the SPA will be composed.

### Component

Component is one route in the Vue.js SPA, each separate components adds one tab into the navbar. Components don't share data between each other. BE returns a list of information about each component that should appear in the SPA. This information is composed of the following parts:

- `name`: unique name that distinguishes the component between the others
- `title`: the title that should appear in the navbar
- `default_fetch_path`: the url from which the component will lazily download the information needed to be ran.

### Default Component

The component that appears first in the list returned by BE is set to be the default component and will immediately start to fetch its configuration.

## Fetch Component Configuration
