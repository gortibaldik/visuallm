from typing import List

from visuallm.components.GenerationComponent import InteractiveGenerationComponent
from visuallm.elements.element_base import ElementBase

from .input_display import PersonaChatVisualization


class Generation(InteractiveGenerationComponent, PersonaChatVisualization):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_model_change_callback()

    def init_model_input_display(self) -> List[ElementBase]:
        return PersonaChatVisualization.init_model_input_display(self)

    def update_model_input_display(self):
        PersonaChatVisualization.update_model_input_display(self, add_target=False)

    def create_model_inputs(self):
        return self._tokenizer(
            self.intial_context_raw_element.content, return_tensors="pt"
        )

    def create_target_encoding(self):
        target = self.get_target_str()
        return self._tokenizer(
            self.intial_context_raw_element.content + " " + target, return_tensors="pt"
        ).input_ids

    def get_target_str(self):
        return self._loaded_sample["history"][-1]
