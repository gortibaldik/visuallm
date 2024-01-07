import time

from visuallm import ComponentBase
from visuallm.elements import ButtonElement, PlainTextElement
from visuallm.elements.collapsible_element import CollapsibleElement
from visuallm.elements.selector_elements import ChoicesSubElement, MinMaxSubElement

N_SECONDS_WAIT = 3


class ComponentWithSubcomponents(ComponentBase):
    def __init__(self):
        super().__init__(name="component_with_subcomponents", title="Subcomponents")
        self._value = 0
        self._plain_text_format = "This is displayed in the collapsible element. Update: {:d}. MinMax: {:d}. Choices: {}"
        self.min_max_element = MinMaxSubElement(0, 10, "Select Number")
        self.choices_element = ChoicesSubElement(
            ["first", "second", "third", "fourth", "fifth", "sixth"], "Select something"
        )
        self.choices_element_2 = ChoicesSubElement(
            ["first_2", "second_2", "third_2", "fourth_2", "fifth_2", "sixth_2"],
            "Select something",
        )
        self.plain_text_element = PlainTextElement(
            content=self._plain_text_format.format(
                self._value,
                self.min_max_element.value_on_backend,
                self.choices_element.value_on_backend,
            )
        )
        self.add_element(
            CollapsibleElement(
                title="Show Button",
                subelements=[
                    ButtonElement(
                        self.increase_count,
                        button_text="Increase Count",
                        subelements=[
                            self.min_max_element,
                            self.choices_element,
                            self.choices_element_2,
                        ],
                    )
                ],
            )
        )
        self.add_element(
            CollapsibleElement(title="Show Text", subelements=[self.plain_text_element])
        )
        self.add_element(
            CollapsibleElement(
                title="This Element is by Default Expanded",
                subelements=[
                    PlainTextElement(
                        "You can set the collapsible element to be expanded by default by setting `is_collapsible = True`\n"
                        f"*Beware* if the selected number is `10`, then a wait of {N_SECONDS_WAIT} seconds happens before "
                        "returning the response."
                    )
                ],
                is_collapsed=False,
            )
        )

    def increase_count(self):
        if self.min_max_element.value_from_frontend == 10:
            time.sleep(N_SECONDS_WAIT)
        self._value += 1
        self.plain_text_element.content = self._plain_text_format.format(
            self._value,
            self.min_max_element.value_from_frontend,
            self.choices_element.value_from_frontend,
        )
