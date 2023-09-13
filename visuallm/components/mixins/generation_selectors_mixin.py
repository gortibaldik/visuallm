from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
    SelectorSubElement,
)


@dataclass
class CheckBoxSelectorType:
    default_value: bool


@dataclass
class MinMaxSelectorType:
    min: Union[int, float]
    max: Union[int, float]
    default_value: Optional[Union[int, float]] = None
    step_size: Union[int, float] = 1


@dataclass
class ChoicesSelectorType:
    values: List[str]


SELECTORS_TYPE = Dict[
    str,
    Union[
        MinMaxSelectorType,
        ChoicesSelectorType,
        CheckBoxSelectorType,
    ],
]


class GenerationSelectorsMixin(ABC):
    def __init__(
        self,
        selectors: SELECTORS_TYPE,
    ):
        """This mixin adds Selectors of one of specified types into the frontend.
        The selected attributes are made available in
        `self.selected_generation_parameters`, with keys being the same as the
        ones in the `selectors` argument.


        Args:
            selectors (SELECTORS_TYPE): dictionary of all the selectors which should
                be displayed on the frontend.
        """
        self.generation_selectors: List[SelectorSubElement] = []
        self.name_generation_selector_mapping: Dict[str, SelectorSubElement] = {}

        for selector_name, val in selectors.items():
            selector_text = str(selector_name)
            if not selector_text.rstrip().endswith(":"):
                selector_text = selector_text.rstrip() + ":"
            if isinstance(val, CheckBoxSelectorType):
                selector = CheckBoxSubElement(selector_text, val.default_value)
            elif isinstance(val, MinMaxSelectorType):
                selector = MinMaxSubElement(
                    sample_min=val.min,
                    sample_max=val.max,
                    text=selector_text,
                    step_size=val.step_size,
                    default_value=val.default_value,
                )
            elif isinstance(val, ChoicesSelectorType):
                selector = ChoicesSubElement(val.values, selector_text)
            else:
                raise ValueError(
                    "Only ChoicesSelectorType, MinMaxSelectorType and "
                    + "CheckBoxSelectorType are valid types for the "
                    + "selectors dictionary"
                )
            self.generation_selectors.append(selector)
            self.name_generation_selector_mapping[selector_name] = selector

        self.generation_heading = PlainTextElement(
            content="Generation Parameters", is_heading=True
        )
        self.generation_selector_button = ButtonElement(
            button_text="Send Generation Configuration",
            processing_callback=self.on_generation_changed_callback,
            subelements=self.generation_selectors,
        )

    @property
    def generation_elements(self) -> List[ElementBase]:
        """Elements which change the generation hyperparameters."""
        return [self.generation_heading, self.generation_selector_button]

    @property
    def selected_generation_parameters(self) -> Dict[str, Any]:
        """Currently selected generation parameters, with the keys being the
        same as in the `selectors` argument to the `__init__` method.
        """
        return {
            name: value.selected
            for name, value in self.name_generation_selector_mapping.items()
        }

    @abstractmethod
    def on_generation_changed_callback(self):
        """What to do right after the generation selectors are updated"""
        ...
