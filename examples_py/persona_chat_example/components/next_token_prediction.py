from visuallm.components.NextTokenPredictionComponent import (
    NextTokenPredictionComponent,
)
from visuallm.elements import HeadingElement, PlainTextElement

from .input_display import PersonaChatVisualization


class NextTokenPrediction(NextTokenPredictionComponent, PersonaChatVisualization):
    def __post_init__(self):
        self.after_on_generator_change_callback()

    def init_model_input_display_elements(self):
        expected_outputs_raw_heading = HeadingElement(content="Expected Output")
        self.expected_outputs_raw_element = PlainTextElement()
        return [
            *PersonaChatVisualization.init_dialogue_vis_elements(self),
            *super().init_model_input_display_elements(),
            expected_outputs_raw_heading,
            self.expected_outputs_raw_element,
        ]

    def update_model_input_display_on_sample_change(self):
        super().update_model_input_display_on_sample_change()
        PersonaChatVisualization.update_dialogue_structure_display(
            self, add_target=False
        )
        self.expected_outputs_raw_element.content = self.loaded_sample["candidates"][-1]
