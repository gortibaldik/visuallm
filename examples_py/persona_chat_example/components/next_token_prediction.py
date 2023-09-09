from visuallm.components.NextTokenPredictionComponent import (
    NextTokenPredictionComponent,
)
from visuallm.elements.plain_text_element import PlainTextElement

from .input_display import PersonaChatVisualization


class NextTokenPrediction(NextTokenPredictionComponent, PersonaChatVisualization):
    def after_init_callback(self):
        self.on_model_change_callback()

    def init_model_input_display_elements(self):
        self.expected_outputs_raw_heading = PlainTextElement(
            is_heading=True, content="Expected Output"
        )
        self.expected_outputs_raw_element = PlainTextElement()
        return [
            *PersonaChatVisualization.init_model_input_display(self),
            # self.expected_outputs_raw_heading,
            # self.expected_outputs_raw_element,
        ]

    def update_model_input_display_on_selected_token(self, detokenized_token: str):
        self.input_content.content += detokenized_token

    def update_model_input_display_on_sample_change(self):
        PersonaChatVisualization.update_model_input_display(self, add_target=False)
        self.expected_outputs_raw_element.content = self.loaded_sample["candidates"][-1]

    def create_model_inputs(self):
        return self._tokenizer(self.input_content.content, return_tensors="pt")
