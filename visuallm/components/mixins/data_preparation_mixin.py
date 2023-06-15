from typing import (  # noqa
    Any,
    Callable,
    Dict,
    KeysView,
    List,
    Optional,
    Protocol,
    Union,
)

from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    ChoicesSubElement,
    MinMaxSubElement,
)


class DatasetProtocol(Protocol):
    def __getitem__(self, __key: str) -> List[Any]:
        ...

    def keys(self) -> KeysView[str]:
        ...


DATASET_TYPE = Union[DatasetProtocol, Callable[[], DatasetProtocol]]
DATASETS_TYPE = Union[
    Dict[str, DatasetProtocol],
    Dict[str, Callable[[], DatasetProtocol]],
]


class DataPreparationMixin:
    def __init__(
        self,
        on_sample_change_callback: Callable[[], None],
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
        keep_datasets_in_memory: bool = True,
        update_on_data_config_sent: bool = True,
    ):
        self._dataset, self._dataset_choices = None, None
        if dataset_choices is not None:
            assert len(dataset_choices) != 0
            self._dataset_choices = dataset_choices
            values = dataset_choices.values()
            self._dataset = self.load_dataset(next(iter(values)))

        if dataset is not None and dataset_choices is None:
            assert dataset_choices is None
            self._dataset_choices = None
            self._dataset = self.load_dataset(dataset)

        if keep_datasets_in_memory:
            self._dataset_cache: Optional[Dict[str, DatasetProtocol]] = {}
        else:
            self._dataset_cache = None
        self.initialize_data_button()
        self._on_sample_change_callback = on_sample_change_callback
        self._loaded_sample: Any = self.get_split()[
            int(self.sample_selector_element.selected)
        ]
        self._update_on_data_config_sent = update_on_data_config_sent

    def data_force_update(self):
        self.dataset_split_selector_element.force_set_updated()
        self.sample_selector_element.force_set_updated()
        if self.dataset_selector_element is not None:
            self.dataset_selector_element.force_set_updated()

    def load_dataset(
        self, value: Union[DatasetProtocol, Callable[[], DatasetProtocol]]
    ):
        if callable(value):
            return value()
        else:
            return value

    def load_cached_dataset(
        self, name: str, load_dataset_fn: Callable[[], DatasetProtocol]
    ):
        if self._dataset_cache is not None and name in self._dataset_cache:
            self._dataset = self._dataset_cache[name]
        else:
            self._dataset = load_dataset_fn()
            if self._dataset_cache is not None:
                self._dataset_cache[name] = self._dataset

        self.dataset_split_selector_element.set_choices(
            self.get_dataset_splits(self._dataset)
        )

    def get_dataset_splits(self, dataset: Optional[DatasetProtocol]):
        if dataset is None:
            return ["dummy_split", "dummy_split"]
        return list(dataset.keys())

    def initialize_data_button(self):
        self.dataset_selector_heading = PlainTextElement(
            content="Dataset Settings", is_heading=True
        )
        self.dataset_split_selector_element = ChoicesSubElement(
            choices=self.get_dataset_splits(self._dataset),
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

        self.dataset_button = ButtonElement(
            button_text="Send Dataset Configuration",
            processing_callback=self.dataset_callback,
            subelements=subelements,
        )

    def get_split(self) -> List[Any]:
        if self._dataset is None:
            return ["dummy_sample", "dummy_sample_2"]
        return self._dataset[self.dataset_split_selector_element.selected]

    @property
    def dataset_elements(self):
        return [self.dataset_selector_heading, self.dataset_button]

    def dataset_callback(self):
        """Check `self.sample_selector_element` and
        `self.dataset_split_selector_element` and switch all the associated
        values."""
        assert self._dataset is not None
        if self.dataset_selector_element is not None:
            if self.dataset_selector_element.updated:
                assert self._dataset_choices is not None
                key = self.dataset_selector_element.selected
                args = self._dataset_choices[key]
                self.load_cached_dataset(key, lambda: self.load_dataset(args))
        if self.dataset_split_selector_element.updated:
            self.sample_selector_element._max = len(self.get_split()) - 1
            self.sample_selector_element.selected = min(
                self.sample_selector_element._max,
                self.sample_selector_element.selected,
            )
            self.sample_selector_element.force_set_updated()
        if self.sample_selector_element.updated:
            self._loaded_sample = self.get_split()[
                int(self.sample_selector_element.selected)
            ]
            self._on_sample_change_callback()
        elif self._update_on_data_config_sent:
            self._on_sample_change_callback()
