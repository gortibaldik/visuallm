from llm_generation_server.formatters.format import FormattedContext, Formatter

class PlainFormatter(Formatter):
    def __init__(self, content: str = "", is_heading: bool = False, heading_level=3, **kwargs):
        super().__init__(**kwargs)
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

    def format(self):
        self.changed = False
        return FormattedContext(
            name=self.name,
            type="plain",
            content=dict(
                value=self.content,
                heading=self.is_heading,
                heading_level=self.heading_level
            )
        )
    
    def add_endpoint(self, app):
        pass