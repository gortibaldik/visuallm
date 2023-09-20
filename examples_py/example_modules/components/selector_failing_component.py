from visuallm.component_base import ComponentBase
from visuallm.elements import PlainTextElement
from visuallm.elements.selector_elements import ButtonElement


class SelectorFailingComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="selector_failing_component", title="Failing Selector")
        self.add_elements(
            [
                PlainTextElement(
                    "When you click on the button, the response handler on the backend side raises an exception"
                ),
                ButtonElement(processing_callback=self.on_button_click_raise_exception),
            ]
        )

    def on_button_click_raise_exception(self):
        raise ValueError("Some error occured!")
