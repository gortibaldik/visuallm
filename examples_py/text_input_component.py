from visuallm.component_base import ComponentBase
from visuallm.elements import (
    ButtonElement,
    MainHeadingElement,
    PlainTextElement,
    TextInputElement,
)


class TextInputComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="text_input_component", title="Text Input Component")
        main_heading = MainHeadingElement(content="Text Input Component")
        description_element = PlainTextElement(
            content="""This component implements the following things: you can type something into the text
            input element and click on `Send Text` button and it will display in the text box below and the
            text in the text input area will disappear.

            If you click on `Fill in default text` button, the text input area will contain the text
            reading `This is the default text`.
            """
        )
        self.add_elements([main_heading, description_element])
        self.text_display_element = PlainTextElement(
            content="Nothing has been typed in yet"
        )
        self.text_input_element = TextInputElement(
            processing_callback=self.on_text_sent, button_text="Send Text"
        )
        self.add_element(self.text_display_element)
        self.add_element(self.text_input_element)
        button_element = ButtonElement(
            processing_callback=self.on_button_pressed,
            button_text="Fill in default text",
        )
        self.add_element(button_element)

    def on_text_sent(self):
        self.text_display_element.content = self.text_input_element.text_input
        self.text_input_element.text_input = ""

    def on_button_pressed(self):
        self.text_input_element.text_input = "This is the default text!"
