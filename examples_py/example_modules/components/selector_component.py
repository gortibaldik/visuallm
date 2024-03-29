from visuallm.component_base import ComponentBase
from visuallm.elements import MainHeadingElement, PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    CheckBoxSubElement,
    ChoicesSubElement,
    MinMaxSubElement,
)


class SelectorComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="selector_component", title="Selector Component")
        self.text_element = PlainTextElement()
        self.number_selector_element = MinMaxSubElement(
            sample_min=0, sample_max=10, text="Select Number:"
        )
        self.choices_element = ChoicesSubElement(
            choices=[
                "super",
                "magnificent",
                "incredible",
                "fantastic",
                "unbelievable",
                "terrific",
            ],
            text="This library is:",
        )
        self.checkbox_element = CheckBoxSubElement(text="Have you slept?:")
        self.set_text_element(
            self.choices_element.value_on_backend,
            self.number_selector_element.value_on_backend,
            "First Message",
        )
        self.button_element = ButtonElement(
            processing_callback=self.on_button_clicked,
            subelements=[
                self.number_selector_element,
                self.choices_element,
                self.checkbox_element,
            ],
        )
        self.add_element(MainHeadingElement(content="Selector Component"))
        self.add_elements([self.button_element, self.text_element])

    def on_button_clicked(self):
        n = self.number_selector_element.value_on_backend
        c = self.choices_element.value_on_backend
        message = (
            "I say it as a well-relaxed man!"
            if self.checkbox_element.value_on_backend
            else "Don't take me seriously."
        )
        any_updated = (
            self.number_selector_element.updated
            or self.choices_element.updated
            or self.checkbox_element.updated
        )
        self.set_text_element(c, n, message, any_updated)

    def set_text_element(
        self,
        choice: str,
        number: float,
        message: str,
        any_updated: bool | None = None,
    ):
        self.text_element.content = (
            f"This library is {choice} and I would give "
            f"it {number} stars out of {number} if I could. ({message})"
            + (
                ""
                if any_updated is None
                else f" This {'has' if any_updated else 'has not'} changed!"
            )
        )
