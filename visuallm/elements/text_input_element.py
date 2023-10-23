from collections.abc import Callable

from .element_base import ElementWithEndpoint


class TextInputElement(ElementWithEndpoint):
    def __init__(
        self,
        processing_callback: Callable[[], None],
        name: str = "text_input",
        button_text: str = "Send Text",
        default_text: str = "Type something here",
        blank_text_after_send: bool = True,
    ):
        """Element with textarea input and a button with `button_text`.

        Args:
        ----
            processing_callback (Callable[[], None]): what to do after the user text input is sent
                to the backend
            name (str, optional): unique identifier of the element, if numerous elements share the same name, the library
                internally suffixes the names with suffixes so that the names of all the elements within one components
                are unique . Defaults to "text_input".
            button_text (str, optional): text to display on the button used to send the data. Defaults to "Send Text".
            default_text (str, optional): Placeholder in the textarea. Defaults to "Type something here".
            blank_text_after_send (bool, optional): Whether the text displayed in the text area should be blank after
                sending to the backend. Defaults to True.
        """
        super().__init__(name=name, type="text_input")
        self.processing_callback = processing_callback
        self._text_input = ""
        self._predefined_text_input = ""
        self._button_text = button_text
        self._default_text = default_text
        self._blank_text_after_send = blank_text_after_send

    def endpoint_callback(self):
        response_json = self.get_request_dict()
        self._text_input = response_json["text_input"]
        if self._blank_text_after_send:
            self.predefined_text_input = ""
        else:
            self.predefined_text_input = self._text_input
        self.processing_callback()
        return self.parent_component.fetch_info(fetch_all=False)

    @property
    def text_input(self) -> str:
        """Data that is sent from the user."""
        return self._text_input

    @property
    def predefined_text_input(self) -> str:
        """Data that will be displayed to the user in the textarea of the element."""
        return self._predefined_text_input

    @predefined_text_input.setter
    def predefined_text_input(self, value: str) -> None:
        if value != self._predefined_text_input:
            self._changed = True
        self._predefined_text_input = value

    @property
    def button_text(self) -> str:
        """Text that is displayed in the button on the side of the text box."""
        return self._button_text

    @button_text.setter
    def button_text(self, value: str) -> None:
        self._changed = True
        self._button_text = value

    def construct_element_configuration(self):
        return {
            "button_text": self.button_text,
            "default_text": self._default_text,
            "text_input": self.predefined_text_input,
        }
