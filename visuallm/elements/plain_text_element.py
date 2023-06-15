from .element_base import ElementBase, ElementDescription


class PlainTextElement(ElementBase):
    def __init__(
        self,
        content: str = "",
        is_heading: bool = False,
        heading_level=3,
        name="plain_text",
    ):
        super().__init__(name=name)
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

    def construct_element_description(self):
        self.changed = False
        return ElementDescription(
            name=self.name,
            type="plain",
            configuration=dict(
                value=self.content,
                heading=self.is_heading,
                heading_level=self.heading_level,
            ),
        )

    def add_endpoint(self, app):
        pass
