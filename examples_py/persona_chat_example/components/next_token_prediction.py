from visuallm.components.NextTokenPredictionComponent import (
    NextTokenPredictionComponent,
)
from visuallm.elements.plain_text_element import PlainTextElement

from .input_display import PersonaChatVisualization


class NTP(NextTokenPredictionComponent, PersonaChatVisualization):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_model_change_callback()

    def init_model_input_display(self):
        self.expected_outputs_raw_heading = PlainTextElement(
            is_heading=True, content="Expected Output"
        )
        self.expected_outputs_raw_element = PlainTextElement()
        return [
            self.expected_outputs_raw_heading,
            self.expected_outputs_raw_element,
            *PersonaChatVisualization.init_model_input_display(self),
        ]

    def update_model_input_display_on_selected_token(self, detokenized_token: str):
        self.intial_context_raw_element.content += detokenized_token

    def update_model_input_display_on_sample_change(self):
        PersonaChatVisualization.update_model_input_display(self, add_target=False)
        self.expected_outputs_raw_element.content = self._loaded_sample["history"][-1]

    def create_model_inputs(self):
        return self._tokenizer(
            self.intial_context_raw_element.content, return_tensors="pt"
        )
