from visuallm.component_base import ComponentBase
from visuallm.elements import (
    ButtonElement,
    HeadingElement,
    MainHeadingElement,
    PlainTextElement,
    TextInputElement,
)


class TextInputComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="text_input_component", title="Text Input Component")
        self.add_elements(
            [
                MainHeadingElement(content="Text Input Component"),
                HeadingElement("Text Input Blanks After Send"),
                PlainTextElement(
                    """`Send Text` button fills in the text in the element below. The
                    textarea is blanked out. `Fill in default text` fills the element
                    with some default text."""
                ),
                HeadingElement("Sent Text:", heading_level=4),
            ]
        )
        self.text_display_element_1 = PlainTextElement(
            content="Nothing has been typed in yet"
        )
        self.text_input_blanked_element = TextInputElement(
            processing_callback=self.on_text_sent_blanked,
            button_text="Send Text",
            blank_text_after_send=True,
        )
        self.add_elements(
            [
                self.text_display_element_1,
                self.text_input_blanked_element,
                ButtonElement(
                    processing_callback=self.on_set_default_text_button_pressed,
                    button_text="Fill in default text",
                ),
                HeadingElement("Text Input Stays After Send"),
                PlainTextElement(
                    """`Send Text` button fills in the text in the element below. The
                    textarea stays the same, so the user can edit the text that was
                    previously sent."""
                ),
                HeadingElement("Sent Text:", heading_level=4),
            ]
        )
        self.text_display_element_2 = PlainTextElement(
            content="Nothing has been typed in yet"
        )
        self.text_input_stay_element = TextInputElement(
            processing_callback=self.on_text_sent_stays,
            button_text="Send Text",
            blank_text_after_send=False,
        )
        self.add_elements([self.text_display_element_2, self.text_input_stay_element])

    def on_text_sent_blanked(self):
        self.text_display_element_1.content = self.text_input_blanked_element.text_input

    def on_text_sent_stays(self):
        self.text_display_element_2.content = self.text_input_stay_element.text_input

    def on_set_default_text_button_pressed(self):
        self.text_input_blanked_element.predefined_text_input = (
            "This is the default text!"
        )
