from typing import Callable

from .element_base import ElementWithEndpoint


class TextInputElement(ElementWithEndpoint):
    def __init__(
        self,
        processing_callback: Callable[[], None],
        name: str = "text_input",
        button_text: str = "Send Text",
        default_text: str = "Type something here",
    ):
        super().__init__(name=name, type="text_input")
        self.processing_callback = processing_callback
        self._text_input = ""
        self._button_text = button_text
        self._default_text = default_text

    def endpoint_callback(self):
        response_json = self.get_request_dict()
        self.text_input = response_json["text_input"]
        self.processing_callback()
        return self.parent_component.fetch_info(fetch_all=False)

    @property
    def text_input(self) -> str:
        return self._text_input

    @text_input.setter
    def text_input(self, value: str) -> None:
        if value != self._text_input:
            self._changed = True
        self._text_input = value

    @property
    def button_text(self) -> str:
        """Text that is displayed in the button on the side of the text box."""
        return self._button_text

    @button_text.setter
    def button_text(self, value: str) -> None:
        self._changed = True
        self._button_text = value

    def construct_element_configuration(self):
        return dict(
            button_text=self.button_text,
            default_text=self._default_text,
            text_input=self.text_input,
        )
