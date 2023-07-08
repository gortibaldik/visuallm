from typing import Callable

from flask import request

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
        self.text_input = ""
        self._button_text = button_text
        self._default_text = default_text

    def endpoint_callback(self):
        if not request.is_json:
            raise RuntimeError()
        assert self.parent_component is not None
        response_json = request.get_json()

        self.text_input = response_json["text_input"]
        self.processing_callback()

        assert self.parent_component is not None
        return self.parent_component.fetch_info(fetch_all=False)

    def construct_element_configuration(self):
        return dict(button_text=self._button_text, default_text=self._default_text)
