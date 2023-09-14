from typing import List

from visuallm.components.GenerationComponent import GenerationComponent
from visuallm.elements.element_base import ElementBase

from .input_display import PersonaChatVisualization


class Generation(GenerationComponent, PersonaChatVisualization):
    def __post_init__(self):
        self.after_on_generator_change_callback()

    def init_model_input_display(self) -> List[ElementBase]:
        return [
            *PersonaChatVisualization.init_dialogue_vis_elements(self),
            *super().init_model_input_display(),
        ]

    def update_model_input_display(self):
        super().update_model_input_display()
        PersonaChatVisualization.update_dialogue_structure_display(
            self, add_target=False
        )
