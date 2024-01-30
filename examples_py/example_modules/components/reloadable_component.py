from visuallm.component_base import ComponentBase
from visuallm.elements import (
    CollapsibleElement,
    ElementBase,
    MainHeadingElement,
    PlainTextElement,
)
from visuallm.elements.selector_elements import (
    ButtonElement,
)


class ReloadableComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="reloadable_component", title="Reloadable")
        self.stages = [
            self.stage_1,
            self.stage_2,
        ]
        self.stage_index = -1
        self.create_elements()
        self.reload_page_callback()

    def create_elements(self):
        self.main_heading_element = MainHeadingElement(content="Reload Component")
        self.stage_1_description = PlainTextElement(
            content='When you click on the "Reload" button, the page will reload with new elements.'
        )
        self.stage_2_description = PlainTextElement(
            "The page was reloaded!\n"
            "(Click on `Reload` button in under the `Button Back` to go back to the previous page)"
        )
        self.stage_1_button = ButtonElement(
            processing_callback=self.reload_page_callback,
            button_text="Reload",
            reload_page=True,
        )
        self.stage_2_button_collapsible = CollapsibleElement(
            title="Button Back",
            subelements=[
                ButtonElement(
                    processing_callback=self.reload_page_callback,
                    button_text="Reload",
                    reload_page=True,
                )
            ],
        )
        self.add_elements(
            [
                self.main_heading_element,
                self.stage_1_description,
                self.stage_2_description,
                self.stage_1_button,
                self.stage_2_button_collapsible,
            ]
        )
        self.stage_1_elements: list[ElementBase] = [
            self.main_heading_element,
            self.stage_1_description,
            self.stage_1_button,
        ]
        self.stage_2_elements: list[ElementBase] = [
            self.main_heading_element,
            self.stage_2_description,
            self.stage_2_button_collapsible,
        ]

    def stage_1(self):
        self.clear_elements()
        for element in self.stage_1_elements:
            element.set_displayed()

    def stage_2(self):
        self.clear_elements()
        for element in self.stage_2_elements:
            element.set_displayed()

    def reload_page_callback(self):
        self.stage_index = (self.stage_index + 1) % len(self.stages)
        print("self.stage_index", self.stage_index)
        self.stages[self.stage_index]()
