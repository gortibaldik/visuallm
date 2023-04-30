from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, MutableSet, Optional

from flask import request

from llm_generation_server.server import Server

from .element_base import ElementDescription, ElementWithEndpoint
from .utils import register_named


@dataclass
class SubElementConfiguration:
    subtype: str
    name: str
    configuration: Dict[str, Any]
    parent_name: str


class ButtonElement(ElementWithEndpoint):
    def __init__(
        self,
        name: str = "selector",
        subelements: List[SelectorSubElement] = [],
        button_text="Select",
        **kwargs,
    ):
        """
        Args:
            name (str, optional): name of the element, doesn't have to be
                provided. Defaults to "selector".
            subelements (List[SelectorSubElement], optional): input
                subelements. E.g. if there is a checkbox on each press of a
                button, the checkbox value will be sent to the backend.
                Defaults to [].
            button_text (str, optional): Text displayed in a button input
                element. Defaults to "Select".

        Keyword Args:
            endpoint_callback: the callback function that will be called when
                the user clicks the button on the frontend
        """
        super().__init__(name=name, **kwargs)
        self.type = "sample_selector"
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
        the relevant selected attributes in subelement selectors
        """
        if not request.is_json:
            raise RuntimeError()
        response_json = request.get_json()
        for key, value in response_json.items():
            self._subelements_dict[key].selected = value

    def add_subelement(self, subelement: SelectorSubElement):
        if subelement.parent_element is not None:
            raise RuntimeError()
        subelement.parent_element = self

        register_named(subelement, self._subelement_names, self._subelements)
        self._subelements_dict[subelement.name] = subelement

    def add_endpoint(self, app: Server):
        app.add_endpoint(self.endpoint_url, self.endpoint_callback, methods=["POST"])


class SelectorSubElement(ABC):
    @property
    def subelement_configuration(self) -> SubElementConfiguration:
        if self.parent_element is None:
            raise RuntimeError()
        return SubElementConfiguration(
            self._subtype,
            self.name,
            dict(selected=self._selected, text=self._text, **self._specific_data),
            self.parent_element.name,
        )

    @property
    @abstractmethod
    def _specific_data(self) -> Dict[str, Any]:
        ...

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self.parent_element is None:
            raise ValueError(
                "Cannot change the value of the element without atributing "
                + "the element to the parent component"
            )
        self.parent_element.changed = True
        self._selected = value

    def __init__(self, subtype: str, text: str):
        """WARNING:
        `subtype` must match the subtype field in frontend.
        """
        self.name = str(subtype)
        self._subtype = subtype
        self._selected = None
        self.parent_element: Optional[ButtonElement] = None
        self._text = text


class MinMaxSubElement(SelectorSubElement):
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
        if sample_min >= sample_max:
            raise ValueError(
                f"sample_min ({sample_min}) should be bigger than sample_max "
                + f"({sample_max})"
            )
        if default_value is None:
            default_value = sample_min
        self._selected: float = default_value
        self._min = sample_min
        self._max = sample_max
        self._step_size = step_size

    @SelectorSubElement.selected.setter
    def selected(self, value: float):
        if (value > self._max) or (value < self._min):
            raise ValueError(
                f"Invalid value to selected ({value}) should be in range: ["
                + f"{self._min}, {self._max}]"
            )
        SelectorSubElement.selected.fset(self, value)  # type: ignore

    @property
    def _specific_data(self) -> Dict[str, Any]:
        return dict(min=self._min, max=self._max, step_size=self._step_size)


class ChoicesSubElement(SelectorSubElement):
    def __init__(self, choices: List[str], text: str):
        """Default selected value is the first value in the `choices` list"""
        super().__init__(subtype="choices", text=text)
        if len(choices) == 0:
            raise RuntimeError("choices should have length at least 1!")
        self._selected = choices[0]
        self._choices = choices

    @SelectorSubElement.selected.setter
    def selected(self, value):
        if value not in self._choices:
            raise ValueError(
                f"Invalid value to selected ({value}), "
                + f"possibilities: {self._choices}"
            )
        SelectorSubElement.selected.fset(self, value)  # type: ignore

    @property
    def _specific_data(self) -> Dict[str, Any]:
        return dict(choices=self._choices)


class CheckBoxSubElement(SelectorSubElement):
    def __init__(self, text: str, default_value: bool = False):
        super().__init__(subtype="check_box", text=text)
        self._selected = default_value

    @SelectorSubElement.selected.setter
    def selected(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError(f"Invalid value assigned to bool: {value}")
        SelectorSubElement.selected.fset(self, value)

    @property
    def _specific_data(self) -> Dict[str, Any]:
        return {}
