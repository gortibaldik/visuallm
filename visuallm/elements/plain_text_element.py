from typing import Any

from visuallm.elements.element_base import ElementBase


class PlainTextElement(ElementBase):

    """Display some plain text message to the user on the frontend.

    Allows including newlines, throws exception if any "<" or ">" is
    detected.
    """

    def __init__(
        self,
        content: str = "",
        is_heading: bool = False,
        heading_level=3,
        name="plain_text",
    ):
        super().__init__(name=name, type="plain")
        self._content = content
        self.is_heading = is_heading
        self.heading_level = heading_level

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        value = self._convert_brackets(value)
        value = self._convert_newline_to_br_tags(value)
        if value != self._content:
            self.set_changed()
        self._content = value

    def construct_element_configuration(self) -> dict[str, Any]:
        if not self._is_sane(self.content):
            raise ValueError(
                f"'{self.content}' is not allowed value of PlainText element."
            )
        return {
            "value": self.content,
            "heading": self.is_heading,
            "heading_level": self.heading_level,
        }

    @staticmethod
    def _convert_newline_to_br_tags(value: str):
        value = value.replace("\n", "<br />")
        return value

    @staticmethod
    def _convert_brackets(value: str):
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        return value

    @staticmethod
    def _is_sane(value: str):
        value = value.replace("<br />", "")
        return "<" not in value and ">" not in value


class HeadingElement(PlainTextElement):
    def __init__(self, content: str = "", heading_level=3, name="heading"):
        super().__init__(
            content, is_heading=True, heading_level=heading_level, name=name
        )


class MainHeadingElement(HeadingElement):
    def __init__(self, content: str = "", name="heading"):
        super().__init__(content, heading_level=2, name=name)
