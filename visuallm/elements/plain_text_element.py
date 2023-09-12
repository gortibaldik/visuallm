from typing import Any, Dict

from .element_base import ElementBase


class PlainTextElement(ElementBase):
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
        self._changed = True
        self._content = value

    def construct_element_configuration(self) -> Dict[str, Any]:
        return dict(
            value=self.content,
            heading=self.is_heading,
            heading_level=self.heading_level,
        )


class HeadingElement(PlainTextElement):
    def __init__(self, content: str = "", heading_level=3, name="heading"):
        super().__init__(
            content, is_heading=True, heading_level=heading_level, name=name
        )


class MainHeadingElement(HeadingElement):
    def __init__(self, content: str = "", name="heading"):
        super().__init__(content, heading_level=2, name=name)
