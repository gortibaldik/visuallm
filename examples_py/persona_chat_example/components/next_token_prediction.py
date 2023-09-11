from visuallm.components.NextTokenPredictionComponent import (
    NextTokenPredictionComponent,
)
from visuallm.elements.plain_text_element import PlainTextElement

from .input_display import PersonaChatVisualization


class NextTokenPrediction(NextTokenPredictionComponent, PersonaChatVisualization):
    def __post_init__(self):
        self.on_model_change_callback()

    def init_model_input_display_elements(self):
        self.expected_outputs_raw_heading = PlainTextElement(
            is_heading=True, content="Expected Output"
        )
        self.expected_outputs_raw_element = PlainTextElement()
        return [
            *PersonaChatVisualization.init_model_input_display(self),
            self.expected_outputs_raw_heading,
            self.expected_outputs_raw_element,
        ]

    def update_model_input_display_on_selected_token(self, detokenized_token: str):
        self.text_to_tokenizer_element.content += detokenized_token

    def update_model_input_display_on_sample_change(self):
        PersonaChatVisualization.update_model_input_display(self, add_target=False)
        self.expected_outputs_raw_element.content = self.loaded_sample["candidates"][-1]

    def create_model_inputs(self):
        return self._tokenizer(
            self.text_to_tokenizer_element.content, return_tensors="pt"
        )
