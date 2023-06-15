from heapq import nlargest
from typing import Optional

import torch
from numpy.typing import NDArray
from transformers import PreTrainedModel, PreTrainedTokenizer

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.components.mixins.model_selection_mixin import (
    MODEL_TOKENIZER_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements.barchart_element import BarChartElement
from visuallm.elements.plain_text_element import PlainTextElement


class NextTokenPredictionComponent(
    ComponentBase, ModelSelectionMixin, DataPreparationMixin
):
    def __init__(
        self,
        title: str = "Next Token Prediction",
        model: Optional[PreTrainedModel] = None,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        model_tokenizer_choices: Optional[MODEL_TOKENIZER_CHOICES] = None,
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
        n_largest_tokens_to_return: int = 10,
    ):
        self.main_heading_element = PlainTextElement(
            is_heading=True,
            heading_level=2,
            content=title,
        )
        ModelSelectionMixin.__init__(
            self,
            model_tokenizer_choices=model_tokenizer_choices,
            model=model,
            tokenizer=tokenizer,
            on_model_change_callback=self.on_model_change_callback,
        )
        DataPreparationMixin.__init__(
            self,
            on_sample_change_callback=self.on_sample_change_callback,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        softmax_elements = self.init_softmax_heading_elements()
        input_display_elements = self.init_model_input_display()
        self._n_largest_tokens_to_return = n_largest_tokens_to_return
        self.init_word_vocab()

        super().__init__(
            name="next_token_prediction",
            title=title,
            elements=[
                self.main_heading_element,
                *self.dataset_elements,
                *self.model_elements,
                *input_display_elements,
                *softmax_elements,
            ],
        )

    def init_word_vocab(self):
        vocab_size = len(self._tokenizer.get_vocab())
        self.word_vocab = [""] * vocab_size
        for str_val, int_val in self._tokenizer.get_vocab().items():
            self.word_vocab[int_val] = str_val

    def init_softmax_heading_elements(self):
        self.softmax_heading_element = PlainTextElement(
            content="Next Token Probabilities:", is_heading=True
        )
        self.softmax_element = BarChartElement(
            processing_callback=self.select_next_token,
        )
        return [self.softmax_heading_element, self.softmax_element]

    def init_model_input_display(self):
        self.input_display = PlainTextElement()
        return [self.input_display]

    def update_model_input_display_on_sample_change(self):
        self.input_display.content = self._loaded_sample

    def update_model_input_display_on_selected_token(self, detokenized_token: str):
        self.input_display.content += detokenized_token

    def create_model_inputs(self):
        model_inputs = self._tokenizer(self.input_display.content, return_tensors="pt")
        return model_inputs

    def on_model_change_callback(self):
        self.init_word_vocab()
        self.data_force_update()
        self.dataset_callback()

    def _one_token_prediction(self):
        model_inputs = self.create_model_inputs()
        with torch.no_grad():
            probs: torch.Tensor = self._model(**model_inputs).logits
            probs = torch.softmax(probs, dim=-1)
        np_probs: NDArray = probs[0, -1, :].numpy()
        return np_probs

    def _get_n_largest_tokens_and_probs(self, probs: NDArray):
        return nlargest(
            self._n_largest_tokens_to_return,
            zip(map(lambda x: float(x) * 100, probs), self.word_vocab),
            key=lambda x: x[0],
        )

    def update_softmax_element(self):
        probs = self._one_token_prediction()
        n_largest_probs = self._get_n_largest_tokens_and_probs(probs)

        bar_heights = [[x[0]] for x in n_largest_probs]
        bar_annotations = [[f"{x[0]: .3f}%"] for x in n_largest_probs]
        annotations = [x[1] for x in n_largest_probs]
        self.softmax_element.set_possibilities(
            bar_heights, bar_annotations, annotations
        )

    def select_next_token(self):
        token = self.softmax_element.selected
        detokenized_token = self._tokenizer.convert_tokens_to_string([token])
        self.update_model_input_display_on_selected_token(detokenized_token)
        self.update_softmax_element()

    def on_sample_change_callback(self):
        self.update_model_input_display_on_sample_change()
        self.update_softmax_element()
