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
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self.changed = True
        self._content = value

    def construct_element_configuration(self):
        return dict(
            value=self.content,
            heading=self.is_heading,
            heading_level=self.heading_level,
        )
