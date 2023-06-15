from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, MutableSet, Optional, TypeVar

from flask import request

from visuallm.server import Server

from .element_base import ElementDescription, ElementWithEndpoint
from .utils import register_named


@dataclass
class SubElementConfiguration:
    subtype: str
    name: str
    configuration: Dict[str, Any]
    parent_name: str


class ButtonElement(ElementWithEndpoint):
    """I expect the following flow of data:
    - In frontend the user selects some value from the selector (automatic)
    - In frontend the user clicks the button element which is the parent of
        the selector (automatic)
    - The data arrives to backend, where each selector is updated and signalizes
        that is has been updated through `self.updated` flag (automatic)
    - the programmer can control what is influenced by updated selectors
    - all the changed elements are sent back to the frontend (automatic)
    """

    def __init__(
        self,
        processing_callback: Callable[[], None],
        name: str = "selector",
        subelements: List[SelectorSubElement] = [],
        button_text="Select",
        **kwargs,
    ):
        """
        Args:
            processing_callback (Callable[[], None]): a function that is
                called just after all the data from the frontend have been
                processed.
            name (str, optional): name of the element, doesn't have to be
                provided. Defaults to "selector".
            subelements (List[SelectorSubElement], optional): input
                subelements. E.g. if there is a checkbox on each press of a
                button, the checkbox value will be sent to the backend.
                Defaults to [].
            button_text (str, optional): Text displayed in a button input
                element. Defaults to "Select".
        """
        if "endpoint_callback" not in kwargs:
            kwargs["endpoint_callback"] = self.default_select_callback
        super().__init__(name=name, **kwargs)
        self.type = "sample_selector"
        self.processing_callback = processing_callback
        self._button_text = button_text
        self._subelements_dict: Dict[str, SelectorSubElement] = {}
        self._subelements: List[SelectorSubElement] = []
        self._subelement_names: MutableSet[str] = set()

        for subelement in subelements:
            self.add_subelement(subelement)

    def construct_element_description(self):
        self.changed = False
        return ElementDescription(
            name=self.name,
            type=self.type,
            configuration=dict(
                address=self.endpoint_url.removeprefix("/"),
                button_text=self._button_text,
                subelement_configs=[
                    c.subelement_configuration for c in self._subelements
                ],
            ),
        )

    def default_select_callback(self):
        """Goes over the standard format of response from FE and sets all
        the relevant selected attributes in subelement selectors, hten returns
        the control to the programmer for handling of the updated data and
        then returns everything updated to the frontend.
        """
        if not request.is_json:
            raise RuntimeError()
        assert self.parent_component is not None
        response_json = request.get_json()
        for key, value in response_json.items():
            self._subelements_dict[key].selected = value

        self.processing_callback()
        return self.parent_component.fetch_info(fetch_all=False)

    def add_subelement(self, subelement: SelectorSubElement):
        if subelement.parent_element is not None:
            raise RuntimeError()
        subelement.parent_element = self

        register_named(subelement, self._subelement_names, self._subelements)
        self._subelements_dict[subelement.name] = subelement

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])


SelectedType = TypeVar("SelectedType")


class SelectorSubElement(ABC, Generic[SelectedType]):
    """I expect the following flow of data:
    - In frontend the user selects some value from the selector (automatic)
    - In frontend the user clicks the button element which is the parent of
        the selector (automatic)
    - The data arrives to backend, where each selector is updated and signalizes
        that is has been updated through `self.updated` flag (automatic)
    - the programmer can control what is influenced by updated selectors
    - all the changed elements are sent back to the frontend (automatic)
    """

    @property
    def subelement_configuration(self) -> SubElementConfiguration:
        if self.parent_element is None:
            raise RuntimeError()
        return SubElementConfiguration(
            self._subtype,
            self.name,
            dict(
                selected=self._selected,
                text=self._text,
                **self.construct_selector_data(),
            ),
            self.parent_element.name,
        )

    @abstractmethod
    def construct_selector_data(self) -> Dict[str, Any]:
        ...

    @property
    @abstractmethod
    def selected(self):
        ...

    @selected.setter
    @abstractmethod
    def selected(self, value: SelectedType):
        ...

    def selected_getter(self) -> SelectedType:
        assert self._selected is not None
        return self._selected

    def selected_setter(self, value: SelectedType):
        if self.parent_element is None:
            raise ValueError(
                "Cannot change the value of the element without atributing "
                + "the element to the parent component"
            )
        self._updated = value != self._selected
        self.parent_element.changed |= self._updated
        self._selected = value

    def force_set_updated(self):
        """Set updated to true, so that any changes associated with the update
        are triggered"""
        self._updated = True

    @property
    def updated(self):
        """Whether the selector was updated by the frontend."""
        return self._updated

    def __init__(self, subtype: str, text: str):
        """WARNING:
        `subtype` must match the subtype field in frontend.
        """
        self.name = str(subtype)
        self._updated = True
        self._subtype = subtype
        self._selected: Optional[SelectedType] = None
        self.parent_element: Optional[ButtonElement] = None
        self._text = text


class MinMaxSubElement(SelectorSubElement[float]):
    """Subelement in the ButtonElement that creates an int selection in
    a range. E.g. selector between [min, max].
    """

    def __init__(
        self,
        sample_min: float,
        sample_max: float,
        text: str,
        step_size: float = 1.0,
        default_value: Optional[float] = None,
    ):
        super().__init__(subtype="min_max", text=text)
        if sample_min > sample_max:
            raise ValueError(
                f"sample_min ({sample_min}) should be bigger than or equal "
                f"to sample_max ({sample_max})"
            )
        if default_value is None:
            default_value = sample_min
        self._selected: float = default_value
        self._min = sample_min
        self._max = sample_max
        self._step_size = step_size

    @property
    def selected(self):
        return self.selected_getter()

    @selected.setter
    def selected(self, value: float):
        if (value > self._max) or (value < self._min):
            raise ValueError(
                f"Invalid value to selected ({value}) should be in range: ["
                + f"{self._min}, {self._max}]"
            )
        self.selected_setter(value)

    def construct_selector_data(self) -> Dict[str, Any]:
        self._updated = False
        return dict(min=self._min, max=self._max, step_size=self._step_size)


class ChoicesSubElement(SelectorSubElement[str]):
    def __init__(self, choices: List[str], text: str):
        """Default selected value is the first value in the `choices` list"""
        super().__init__(subtype="choices", text=text)
        if len(choices) == 0:
            raise RuntimeError("choices should have length at least 1!")
        self._selected = choices[0]
        self._choices = choices

    @property
    def selected(self):
        return self.selected_getter()

    @selected.setter
    def selected(self, value: str):
        if value not in self._choices:
            raise ValueError(
                f"Invalid value to selected ({value}), "
                + f"possibilities: {self._choices}"
            )
        self.selected_setter(value)

    def set_choices(self, new_choices: List[str]):
        if len(new_choices) == 0:
            raise RuntimeError("Choices should have length at least 1!")
        self._choices = new_choices
        if self._selected not in self._choices:
            self._selected = self._choices[0]
        self.force_set_updated()

    def construct_selector_data(self) -> Dict[str, Any]:
        self._updated = False
        return dict(choices=self._choices)


class CheckBoxSubElement(SelectorSubElement[bool]):
    def __init__(self, text: str, default_value: bool = False):
        super().__init__(subtype="check_box", text=text)
        self._selected = default_value

    @property
    def selected(self):
        return self.selected_getter()

    @selected.setter
    def selected(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"Invalid value assigned to bool: {value}")
        self.selected_setter(value)

    def construct_selector_data(self) -> Dict[str, Any]:
        self._updated = False
        return {}
