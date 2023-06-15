import time

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
        self.text_element = PlainTextElement(content="Nothing was selected")
        self.number_selector_element = MinMaxSubElement(
            sample_min=0, sample_max=10, text="Select Number:"
        )
        self.choices_element = ChoicesSubElement(
            choices=["super", "magnificent", "incredible"], text="This library is:"
        )
        self.checkbox_element = CheckBoxSubElement(text="Have you slept?:")
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
        b = (
            "I say it as a well-relaxed man!"
            if self.checkbox_element.selected
            else "Don't take me seriously."
        )
        any_updated = (
            self.number_selector_element.updated
            or self.choices_element.updated
            or self.checkbox_element.updated
        )
        self.text_element.content = (
            f"This library is {c} and I would give "
            + f"it {n} stars out of {n} if I could. ({b})"
            + f" This {'has' if any_updated else 'has not'} changed!"
        )
        time.sleep(n)
