import time
from typing import Optional

from visuallm.component_base import ComponentBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
)


class SelectorComponent(ComponentBase):
    def __init__(self):
        self.text_element = PlainTextElement()
        self.number_selector_element = MinMaxSubElement(
            sample_min=0, sample_max=10, text="Select Number:"
        )
        self.choices_element = ChoicesSubElement(
            choices=["super", "magnificent", "incredible"], text="This library is:"
        )
        self.checkbox_element = CheckBoxSubElement(text="Have you slept?:")
        self.set_text_element(
            self.choices_element.selected,
            self.number_selector_element.selected,
            "First Message",
        )
        self.button_element = ButtonElement(
            processing_callback=self.button_clicked,
            subelements=[
                self.number_selector_element,
                self.choices_element,
                self.checkbox_element,
            ],
        )
        super().__init__(
            name="selector_component",
            title="Selector Component",
            elements=[
                PlainTextElement(
                    is_heading=True, heading_level=2, content="Selector Component"
                ),
                self.button_element,
                self.text_element,
            ],
        )

    def button_clicked(self):
        n = self.number_selector_element.selected
        c = self.choices_element.selected
        message = (
            "I say it as a well-relaxed man!"
            if self.checkbox_element.selected
            else "Don't take me seriously."
        )
        any_updated = (
            self.number_selector_element.updated
            or self.choices_element.updated
            or self.checkbox_element.updated
        )
        self.set_text_element(c, n, message, any_updated)
        time.sleep(n)

    def set_text_element(
        self,
        choice: str,
        number: float,
        message: str,
        any_updated: Optional[bool] = None,
    ):
        self.text_element.content = (
            f"This library is {choice} and I would give "
            + f"it {number} stars out of {number} if I could. ({message})"
            + (
                ""
                if any_updated is None
                else f" This {'has' if any_updated else 'has not'} changed!"
            )
        )
