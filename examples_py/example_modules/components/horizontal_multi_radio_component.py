from visuallm import ComponentBase
from visuallm.elements import PlainTextElement
from visuallm.elements.selector_elements import (
    ButtonElement,
    MultiRadioSubElement,
)


class HorizontalMultiRadioComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="hmr_subcomponent", title="Horizontal Multi Radio")
        self.plain_text = PlainTextElement()
        self.multiselect = MultiRadioSubElement(
            choices=[f"choice{i}" for i in range(5)],
            text="Select an Option:",
            is_horizontal=True,
            deselect=True,
        )
        button_element = ButtonElement(
            processing_callback=self.on_button_press,
            subelements=[
                self.multiselect,
            ],
        )
        self.add_element(button_element)
        self.add_element(self.plain_text)

        self.plain_text_2 = PlainTextElement()
        self.multiselect_2 = MultiRadioSubElement(
            choices=[f"choice{i}" for i in range(5)],
            text="Select an Option:",
            is_horizontal=True,
            deselect=False,
        )
        button_element_2 = ButtonElement(
            processing_callback=self.on_button_2_press, subelements=[self.multiselect_2]
        )
        self.add_element(button_element_2)
        self.add_element(self.plain_text_2)
        self.on_button_press()
        self.on_button_2_press()

    def on_button_press(self):
        self.plain_text.content = (
            f"Last selected option: '{self.multiselect.value_from_frontend}'"
        )

    def on_button_2_press(self):
        self.plain_text_2.content = (
            f"Last selected option: '{self.multiselect_2.value_from_frontend}'"
        )
