from typing import Any, Callable, Dict, List, Tuple, Union

from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
    SelectorSubElement,
)

SELECTORS_TYPE = Dict[
    str,
    Union[
        Tuple[int, int],
        Tuple[int, int, int],
        Tuple[float, float, float],
        Tuple[float, float, float, float],
        List[str],
        bool,
    ],
]


class GenerationSelectorsMixin:
    def __init__(
        self,
        selectors: SELECTORS_TYPE,
        on_generation_changed_callback: Callable[[], None],
    ):
        self.generation_selectors: List[SelectorSubElement] = []
        self.name_generation_selector_mapping: Dict[str, SelectorSubElement] = {}

        for selector_name, val in selectors.items():
            selector_text = str(selector_name)
            if not selector_text.rstrip().endswith(":"):
                selector_text = selector_text.rstrip() + ":"
            if isinstance(val, bool):
                selector = CheckBoxSubElement(selector_text, val)
            elif isinstance(val, tuple):
                if len(val) == 2:
                    selector = MinMaxSubElement(val[0], val[1], selector_text)
                elif len(val) == 3:
                    if isinstance(val[0], int):
                        selector = MinMaxSubElement(
                            val[0], val[1], selector_text, default_value=val[2]
                        )
                    else:
                        selector = MinMaxSubElement(
                            val[0], val[1], selector_text, step_size=val[2]
                        )
                elif len(val) == 4:
                    selector = MinMaxSubElement(
                        val[0],
                        val[1],
                        selector_text,
                        step_size=val[2],
                        default_value=val[3],
                    )
                else:
                    raise ValueError()
            elif isinstance(val, list):
                selector = ChoicesSubElement(val, selector_text)
            else:
                raise ValueError()
            self.generation_selectors.append(selector)
            self.name_generation_selector_mapping[selector_name] = selector

        self.generation_heading = PlainTextElement(
            content="Generation Parameters", is_heading=True
        )
        self._on_generation_changed_callback = on_generation_changed_callback
        self.generation_selector_button = ButtonElement(
            button_text="Send Generation Configuration",
            processing_callback=self._on_generation_changed_callback,
            subelements=self.generation_selectors,
        )

    @property
    def generation_elements(self):
        return [self.generation_heading, self.generation_selector_button]

    @property
    def selected_generation_parameters(self) -> Dict[str, Any]:
        return {
            name: value.selected
            for name, value in self.name_generation_selector_mapping.items()
        }

    def generation_callback(self):
        self._on_generation_changed_callback()
