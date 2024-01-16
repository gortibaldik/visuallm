from visuallm import ComponentBase
from visuallm.elements import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    MultiRadioSubElement,
)


class HorizontalMultiRadioComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="hmr_subcomponent", title="Horizontal Multi Radio")
        self.multiselect = MultiRadioSubElement(
            [f"choice{i}" for i in range(5)], "Select an Option:", is_horizontal=True
        )
        self.plain_text = PlainTextElement()
        button_element = ButtonElement(
            processing_callback=self.on_button_press,
            subelements=[
                self.multiselect,
            ],
        )
        self.add_element(button_element)
        self.add_element(self.plain_text)
        self.on_button_press()

    def on_button_press(self):
        self.plain_text.content = (
            f"Last selected option: '{self.multiselect.value_from_frontend}'"
        )
