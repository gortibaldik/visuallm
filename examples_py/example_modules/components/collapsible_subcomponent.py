from visuallm import ComponentBase
from visuallm.elements import ButtonElement, PlainTextElement
from visuallm.elements.collapsible_element import CollapsibleElement


class ComponentWithSubcomponents(ComponentBase):
    def __init__(self):
        super().__init__(name="component_with_subcomponents", title="Subcomponents")
        self._value = 0
        self._plain_text_format = (
            "This is displayed in the collapsible element. Update: {:d}"
        )
        self.plain_text_element = PlainTextElement(
            content=self._plain_text_format.format(self._value)
        )
        self.add_element(
            CollapsibleElement(
                title="Show Button",
                subelements=[
                    ButtonElement(self.increase_count, button_text="Increase Count")
                ],
            )
        )
        self.add_element(
            CollapsibleElement(title="Show Text", subelements=[self.plain_text_element])
        )

    def increase_count(self):
        self._value += 1
        self.plain_text_element.content = self._plain_text_format.format(self._value)
