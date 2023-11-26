from abc import ABC, abstractmethod
from collections.abc import Callable, KeysView, Mapping, Sequence
from typing import Any, Protocol

from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    ChoicesSubElement,
    MinMaxSubElement,
    SelectorSubElement,
)


class DatasetProtocol(Protocol):
    def __getitem__(self, __key) -> Any:
        ...

    def keys(self) -> KeysView[str]:
        ...


DATASET_TYPE = DatasetProtocol | Callable[[], DatasetProtocol]
DATASETS_TYPE = (
    Mapping[str, DatasetProtocol] | Mapping[str, Callable[[], DatasetProtocol]]
)


class DataPreparationMixin(ABC):
    def __init__(
        self,
        dataset: DATASET_TYPE | None = None,
        dataset_choices: DATASETS_TYPE | None = None,
        keep_datasets_in_memory: bool = True,
        update_on_data_config_sent: bool = True,
    ):
        """Mixin that implements dataset handling server methods. Each time the new sample
        is selected the mixin automatically loads a sample from the dataset according
        to the configuration send from the frontend.

        Initializes a heading with text "Dataset Settings" and a selector
        element, which contains:
        - selector for specific sample number
        - selector for specific sample split
        - if multiple dataset were provided, a selector for specific dataset

        Warning:
        -------
            You should either provide the dataset or dataset choices, not both at once.

        Args:
        ----
            dataset (Optional[DATASET_TYPE], optional): Dataset or a function that loads
                the dataset. Defaults to None.
            dataset_choices (Optional[DATASETS_TYPE], optional): Dictionary of datasets, or
                dictionary of functions that load the dataset. Defaults to None.
            keep_datasets_in_memory (bool, optional): Whether to load the dataset to cache,
                so that when a new dataset is selected from the frontend, the old one is kept
                in the cache, which makes switching between datasets faster. Defaults to True.
            update_on_data_config_sent (bool, optional): Whether to trigger
                `on_sample_change_callback` even when the config sent from the frontend is exactly
                the same as what is already loaded. May be used for send as restart functionality,
                Defaults to True.
        """
        self._dataset_choices: DATASETS_TYPE | None = None
        self._dataset: DatasetProtocol | None = None

        if keep_datasets_in_memory:
            self._dataset_cache: dict[str, DatasetProtocol] | None = {}
        else:
            self._dataset_cache = None

        if dataset_choices is not None and dataset is None:
            if len(dataset_choices) == 0:
                raise ValueError("Cannot specify dataset_choices with zero length!")
            self._dataset_choices = dataset_choices
            keys = dataset_choices.keys()
            default_dataset_key = next(iter(keys))

            def load_dataset_fn():
                if dataset_choices is None:
                    raise RuntimeError("Dataset choices became None!")
                return self.load_dataset(dataset_choices[default_dataset_key])

            name = default_dataset_key

        elif dataset is not None and dataset_choices is None:
            self._dataset_choices = None

            def load_dataset_fn():
                if dataset is None:
                    raise RuntimeError("Dataset became None!")
                return self.load_dataset(dataset)

            name = None

        else:
            raise ValueError(
                "Cannot specify / not specify both dataset and dataset_choices!"
            )

        self.load_cached_dataset(
            load_dataset_fn=load_dataset_fn, name=name, update_selectors=False
        )
        self.initialize_data_button()
        self._loaded_sample: Any = self.get_split()[
            int(self.sample_selector_element.value_on_backend)
        ]
        self._update_on_data_config_sent = update_on_data_config_sent

    def force_set_dataset_selector_updated(self):
        """Set all the components to "updated" state, so that the dataset
        is reloaded, and the samples are reloaded on next `dataset_callback`
        """
        self.dataset_split_selector_element.force_set_updated()
        self.sample_selector_element.force_set_updated()
        if self.dataset_selector_element is not None:
            self.dataset_selector_element.force_set_updated()

    @staticmethod
    def load_dataset(
        dataset_constructor: DatasetProtocol | Callable[[], DatasetProtocol]
    ) -> DatasetProtocol:
        """Load the dataset using the provided `dataset_constructor`

        Args:
        ----
            dataset_constructor (Union[DatasetProtocol, Callable[[], DatasetProtocol]]): either the dataset
                or a function that loads the dataset.

        Returns:
        -------
            DatasetProtocol: loaded dataset
        """
        if callable(dataset_constructor):
            return dataset_constructor()
        else:
            return dataset_constructor

    def load_cached_dataset(
        self,
        load_dataset_fn: Callable[[], DatasetProtocol],
        name: str | None = None,
        update_selectors: bool = True,
    ):
        """The behavior of this function depends on whether the caching is set or unset.

        If set, the function at first checks whether the dataset with `name` is already
        in the cache and skips the loading and returns the cached value, or if it isn't
        then it loads the dataset, stores it into the cache and returns.

        If unset, the function just loads the dataset and returns it.

        Important:
        ---------
            The loaded dataset is stored in the property: `self.dataset`

        Args:
        ----
            name (str): name of the dataset, the dataset will be stored in the cache under
                this name.
            load_dataset_fn (Callable[[], DatasetProtocol]): function that loads the dataset.
            update_selectors (bool): update dataset selector elements after dataset change
        """
        if self._dataset_cache is not None and name in self._dataset_cache:
            self._dataset = self._dataset_cache[name]
        else:
            self._dataset = load_dataset_fn()
            if self._dataset_cache is not None and name is not None:
                self._dataset_cache[name] = self._dataset

        if update_selectors:
            self.dataset_split_selector_element.set_choices(self.get_dataset_splits())
            self._set_dataset_button_subelements()
            self._update_after_split_change()

    @property
    def dataset(self):
        """Currently loaded dataset"""
        return self._dataset

    @property
    def loaded_sample(self):
        """Currently loaded sample"""
        return self._loaded_sample

    @property
    def dataset_choice_elements(self) -> list[ElementBase]:
        """Elements that allow user to select dataset, dataset split, and dataset sample."""
        return [self.dataset_selector_heading, self.dataset_button]

    def _update_after_split_change(self):
        """When dataset split is updated then the sample selector
        needs to be readjusted (e.g. the number of samples in different
        splits can be variable, hence, we need to readjust the max, and
        the selected sample number may be bigger than max, so we need to
        reset selected sample number)
        """
        self.sample_selector_element._max = len(self.get_split()) - 1
        self.sample_selector_element.value_on_backend = min(
            self.sample_selector_element._max,
            self.sample_selector_element.value_on_backend,
        )
        self.sample_selector_element.force_set_updated()

    def get_dataset_splits(self):
        """Return splits of the currently loaded dataset.

        Note:
        ----
            if the dataset is not set yet, returns dummy values

        Returns:
        -------
            List[str]: split names
        """
        if self.dataset is None:
            raise ValueError("dataset is none cannot return its splits!")
        return list(self.dataset.keys())

    def _set_dataset_button_subelements(self) -> None:
        subelements: list[SelectorSubElement] = []

        if len(self.dataset_split_selector_element) > 1:
            subelements.append(self.dataset_split_selector_element)

        subelements.append(self.sample_selector_element)
        if self.dataset_selector_element is not None:
            subelements.append(self.dataset_selector_element)
        self.dataset_button.set_subelements(subelements)

    def initialize_data_button(self):
        """Initializes a heading with text "Dataset Settings" and a selector
        element, which contains:
        - selector for specific sample number
        - selector for specific sample split
        - if multiple dataset were provided, a selector for specific dataset
        """
        self.dataset_selector_heading = PlainTextElement(
            content="Dataset Settings", is_heading=True
        )
        self.dataset_split_selector_element = ChoicesSubElement(
            choices=self.get_dataset_splits(),
            text="Select Dataset Split",
        )
        self.sample_selector_element = MinMaxSubElement(
            sample_min=0,
            sample_max=len(self.get_split()) - 1,
            text="Select Dataset Sample",
        )
        subelements = [
            self.dataset_split_selector_element,
            self.sample_selector_element,
        ]

        if self._dataset_choices is not None:
            self.dataset_selector_element = ChoicesSubElement(
                list(self._dataset_choices.keys()), text="Select Dataset"
            )
            subelements.append(self.dataset_selector_element)
        else:
            self.dataset_selector_element = None

        # register subelements to the dataset button
        self.dataset_button = ButtonElement(
            button_text="Send Dataset Configuration",
            processing_callback=self.on_dataset_change_callback,
            subelements=subelements,
        )
        # set which of the subelements have to be displayed
        self._set_dataset_button_subelements()

    def get_split(self) -> Sequence[Any]:
        """Get all the samples in the currently selected split of the dataset.

        Returns
        -------
            List[Any]: list of samples in the currently selected split of the dataset
        """
        if self.dataset is None:
            return ["dummy_sample", "dummy_sample_2"]
        return self.dataset[self.dataset_split_selector_element.value_on_backend]

    def on_dataset_change_callback(self):
        """Callback that is called each time when a request from frontend comes to
        load a new dataset sample.
        """
        if self.dataset is None:
            raise RuntimeError(
                "`self.dataset` is None, cannot load any new dataset sample!"
            )
        if (self.dataset_selector_element is not None) and (
            self.dataset_selector_element.updated
        ):
            if self._dataset_choices is None:
                raise RuntimeError(
                    "Dataset selector callback called even when no dataset choices are provided!"
                )
            key = self.dataset_selector_element.value_on_backend
            dataset_constructor = self._dataset_choices[key]
            self.load_cached_dataset(
                load_dataset_fn=lambda: self.load_dataset(dataset_constructor),
                name=key,
            )
        if self.dataset_split_selector_element.updated:
            self._update_after_split_change()
        if self.sample_selector_element.updated:
            self._loaded_sample = self.get_split()[
                int(self.sample_selector_element.value_on_backend)
            ]
            self.after_on_dataset_change_callback()
        elif self._update_on_data_config_sent:
            self.after_on_dataset_change_callback()

    @abstractmethod
    def after_on_dataset_change_callback(self) -> None:
        """Callback that is called right after the dataset sample selectors
        are updated and a new sample / dataset is loaded into the
        `self.dataset` and `self.loaded_sample` properties
        """
        ...
