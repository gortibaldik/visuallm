from visuallm.component_base import ComponentBase
from visuallm.elements import (
    ButtonElement,
    HeadingElement,
    MainHeadingElement,
    PlainTextElement,
)
from visuallm.elements.selector_elements import TextInputSubElement


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
        self.text_input_blanked_element = TextInputSubElement(
            blank_after_text_send=True,
        )
        self.button_with_text_input_blanked = ButtonElement(
            processing_callback=self.on_text_sent_blanked,
            button_text="Send Text",
            subelements=[self.text_input_blanked_element],
        )
        self.add_elements(
            [
                self.text_display_element_1,
                self.button_with_text_input_blanked,
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
        self.text_input_stay_element = TextInputSubElement(
            blank_after_text_send=False,
        )
        self.button_with_text_input_stay = ButtonElement(
            processing_callback=self.on_text_sent_stays,
            button_text="Send Text",
            subelements=[self.text_input_stay_element],
        )
        self.add_elements(
            [self.text_display_element_2, self.button_with_text_input_stay]
        )

    def on_text_sent_blanked(self):
        self.text_display_element_1.content = (
            self.text_input_blanked_element.value_from_frontend
        )

    def on_text_sent_stays(self):
        self.text_display_element_2.content = (
            self.text_input_stay_element.value_from_frontend
        )

    def on_set_default_text_button_pressed(self):
        self.text_input_blanked_element.value_on_backend = "This is the default text!"
