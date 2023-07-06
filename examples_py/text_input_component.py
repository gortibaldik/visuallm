from visuallm.component_base import ComponentBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.text_input_element import TextInputElement


class TextInputComponent(ComponentBase):
    def __init__(self):
        self.text_display_element = PlainTextElement(
            content="Nothing has been typed in yet."
        )
        self.text_input_element = TextInputElement(processing_callback=self.text_sent)

        super().__init__(
            name="text_input_component",
            title="Text Input Component",
            elements=[self.text_display_element, self.text_input_element],
        )

    def text_sent(self):
        self.text_display_element.content = self.text_input_element.text_input
