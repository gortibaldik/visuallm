from visuallm.component_base import ComponentBase
from visuallm.elements import CollapsibleElement, MainHeadingElement, PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    ChoicesSubElement,
    MinMaxSubElement,
)


class SelectorChangingComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="selector_change_component", title="Selector Change")
        collapsible = CollapsibleElement(
            title="Description",
            is_collapsed=True,
            subelements=[
                MainHeadingElement(content="Selector Change"),
                PlainTextElement(
                    content='When you click on the "Change" button, the split selector should disappear'
                ),
            ],
        )
        self.add_element(collapsible)

        self.split_selector = ChoicesSubElement(
            choices=["first", "second"], text="Split Selector"
        )
        self.min_max_selector = MinMaxSubElement(
            sample_min=0, sample_max=10, text="Sample Selector"
        )
        self.button_element = ButtonElement(
            processing_callback=lambda: None,
            subelements=[self.split_selector, self.min_max_selector],
        )
        self.change_button_element = ButtonElement(
            processing_callback=self.change_button_callback, button_text="Change"
        )
        self.add_elements([self.button_element, self.change_button_element])

    def change_button_callback(self):
        if len(self.button_element._subelements) == 1:
            self.button_element.set_subelements(
                [
                    self.split_selector,
                    self.min_max_selector,
                ]
            )
        else:
            self.button_element.set_subelements([self.min_max_selector])
        self.button_element.set_changed()
