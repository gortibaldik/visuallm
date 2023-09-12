from visuallm.component_base import ComponentBase
from visuallm.elements import MainHeadingElement, PlainTextElement


class SimpleComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="simple_component", title="Simple Component")
        main_heading_element = MainHeadingElement(content="Really Easy Component")
        self.text_element = PlainTextElement(
            content="""
                Some really interesting text that isn't formatted in any way, it is
                just a plain simple text
            """
        )
        self.add_elements([main_heading_element, self.text_element])
