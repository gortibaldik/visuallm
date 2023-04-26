from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, MutableSet, Optional

from flask import jsonify, request

from llm_generation_server.server import Server

from .element_base import ElementDescription, ElementWithEndpoint
from .utils import register_named


@dataclass
class SubElementConfiguration:
    subtype: str
    name: str
    configuration: Dict[str, Any]
    parent_name: str


class SelectorElement(ElementWithEndpoint):
    def __init__(
        self,
        name: str = "selector",
        subelements: List[SelectorSubElement] = [],
        button_text="Select",
        **kwargs,
    ):
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
                address=self.endpoint_url,
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
            return jsonify(dict(result="failure"))
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
        self.name = str(subtype)
        self._subtype = subtype
        self._selected = None
        self.parent_element: Optional[SelectorElement] = None
        self._text = text


class MinMaxSubElement(SelectorSubElement):
    """Subelement in the SelectorElement that creates an int selection in
    a range. E.g. selector between [min, max].
    """

    def __init__(self, sample_min: int, sample_max: int, text: str):
        super().__init__(subtype="min_max", text=text)
        if sample_min >= sample_max:
            raise ValueError(
                f"sample_min ({sample_min}) should be bigger than sample_max "
                + f"({sample_max})"
            )
        self._selected: int = sample_min
        self._min = sample_min
        self._max = sample_max

    @SelectorSubElement.selected.setter
    def selected(self, value: int):
        if (value > self._max) or (value < self._min):
            raise ValueError(
                f"Invalid value to selected ({value}) should be in range: ["
                + f"{self._min}, {self._max}]"
            )
        SelectorSubElement.selected.fset(self, value)  # type: ignore

    @property
    def _specific_data(self) -> Dict[str, Any]:
        return dict(min=self._min, max=self._max)


class ChoicesSubElement(SelectorSubElement):
    def __init__(self, choices: List[str], text: str):
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