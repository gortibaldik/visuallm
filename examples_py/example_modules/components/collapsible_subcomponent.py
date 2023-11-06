from visuallm import ComponentBase
from visuallm.elements import ButtonElement, PlainTextElement
from visuallm.elements.collapsible_element import CollapsibleElement
from visuallm.elements.selector_elements import MinMaxSubElement


class ComponentWithSubcomponents(ComponentBase):
    def __init__(self):
        super().__init__(name="component_with_subcomponents", title="Subcomponents")
        self._value = 0
        self._plain_text_format = (
            "This is displayed in the collapsible element. Update: {:d}. MinMax: {:d}"
        )
        self.min_max_element = MinMaxSubElement(0, 10, "Select Number")
        self.plain_text_element = PlainTextElement(
            content=self._plain_text_format.format(
                self._value, self.min_max_element.value_on_backend
            )
        )
        self.add_element(
            CollapsibleElement(
                title="Show Button",
                subelements=[
                    ButtonElement(
                        self.increase_count,
                        button_text="Increase Count",
                        subelements=[self.min_max_element],
                    )
                ],
            )
        )
        self.add_element(
            CollapsibleElement(title="Show Text", subelements=[self.plain_text_element])
        )

    def increase_count(self):
        self._value += 1
        self.plain_text_element.content = self._plain_text_format.format(
            self._value, self.min_max_element.value_from_frontend
        )
