from typing import Dict, List, Optional, cast

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from transformers.generation.utils import GenerateOutput
from transformers.tokenization_utils_base import BatchEncoding

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.components.mixins.generation_selectors_mixin import (
    SELECTORS_TYPE,
    GenerationSelectorsMixin,
)
from visuallm.components.mixins.metrics_mixin import (
    GENERATED_TEXT_METRIC,
    PROBS_METRIC,
    MetricsMixin,
)
from visuallm.components.mixins.model_selection_mixin import (
    MODEL_TOKENIZER_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement


class InteractiveGenerationComponent(
    ComponentBase,
    DataPreparationMixin,
    ModelSelectionMixin,
    GenerationSelectorsMixin,
    MetricsMixin,
):
    def __init__(
        self,
        title: str = "Interactive Generation",
        model: Optional[PreTrainedModel] = None,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        model_tokenizer_choices: Optional[MODEL_TOKENIZER_CHOICES] = None,
        metrics_on_generated_text: Dict[str, GENERATED_TEXT_METRIC] = {},
        metrics_on_probs: Dict[str, PROBS_METRIC] = {},
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
        selectors: SELECTORS_TYPE = {},
    ):
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        ModelSelectionMixin.__init__(
            self,
            on_model_change_callback=self.on_model_change_callback,
            model_tokenizer_choices=model_tokenizer_choices,
            model=model,
            tokenizer=tokenizer,
        )
        DataPreparationMixin.__init__(
            self,
            on_sample_change_callback=self.on_sample_change_callback,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        GenerationSelectorsMixin.__init__(
            self,
            selectors=selectors,
            on_generation_changed_callback=self.on_sample_change_callback,
        )
        MetricsMixin.__init__(
            self,
            on_metrics_change=self.on_sample_change_callback,
            metrics_on_generated_text=metrics_on_generated_text,
            metrics_on_probs=metrics_on_probs,
        )
        input_display_elements = self.init_model_input_display()

        super().__init__(
            name="interactive_generation",
            title=title,
            elements=[
                self.main_heading_element,
                *self.dataset_elements,
                *self.model_elements,
                *self.generation_elements,
                *self.metrics_selection,
                *input_display_elements,
                *self.metrics_display,
            ],
        )

    def init_model_input_display(self) -> List[ElementBase]:
        self.input_display = PlainTextElement()
        return [self.input_display]

    def update_model_input_display(self):
        """Updated dataset sample is in `self._loaded_sample`"""
        self.input_display.content = self._loaded_sample

    def create_model_inputs(self):
        context = self.input_display.content
        model_inputs = self._tokenizer(context, return_tensors="pt")
        return model_inputs

    def create_target_encoding(self):
        context = self.input_display.content
        target = context + self.get_target_str()
        model_inputs = self._tokenizer(target, return_tensors="pt")
        return model_inputs.input_ids

    def get_target_str(self) -> str:
        return ""

    def update_generated_output_display(self):
        model_inputs = self.create_model_inputs()
        output = generate_output(
            model_inputs,
            tokenizer=self._tokenizer,
            model=self._model,
            **self.selected_generation_parameters,
        )
        decoded = decode_output(self._tokenizer, model_inputs, output)

        # compute mterics on generated
        probs, output_sequences = measure_output_probability(
            self._model, output.sequences, model_inputs
        )
        self.compute_metrics_on_predicted(
            decoded,
            [self.get_target_str() for _ in range(len(decoded))],
            probs,
            output_sequences,
        )

        # compute scores on target
        probs, output_sequences = measure_output_probability(
            self._model, self.create_target_encoding(), model_inputs
        )
        self.compute_metrics_on_target(self.get_target_str(), probs, output_sequences)

    def on_model_change_callback(self):
        self.data_force_update()
        self.dataset_callback()

    def on_sample_change_callback(self):
        self.update_model_input_display()
        self.update_generated_output_display()


def generate_output(
    model_inputs,
    *,
    tokenizer: PreTrainedTokenizer,
    model: PreTrainedModel,
    **kwargs,
):
    """Returns generated indices and log probabilities of generated indices."""

    # generate with loaded settings
    output = model.generate(
        **model_inputs,
        pad_token_id=tokenizer.eos_token_id,
        output_scores=True,
        return_dict_in_generate=True,
        **kwargs,
    )
    output = cast(GenerateOutput, output)

    return output


def decode_output(
    tokenizer: PreTrainedTokenizer,
    tokenized_inputs: BatchEncoding,
    output: GenerateOutput,
):
    detokenized_outputs = tokenizer.batch_decode(
        output.sequences, skip_special_tokens=True
    )
    detokenized_context = tokenizer.decode(
        tokenized_inputs.input_ids[0], skip_special_tokens=True
    )
    detokenized_outputs = [
        d.removeprefix(detokenized_context) for d in detokenized_outputs
    ]

    return detokenized_outputs


def measure_output_probability(
    model: PreTrainedModel,
    output_sequences: torch.Tensor,
    tokenized_inputs: BatchEncoding,
):
    """
    Returns:
        Tuple[List[float], List[float], List[float]]: log_probs,
            penalty_log_probs, probs
    """
    input_length = tokenized_inputs.input_ids.size(1)
    output_probs_list = []
    output_sequences_list = []
    for i in range(output_sequences.size(0)):
        with torch.no_grad():
            output = model(
                output_sequences[i : i + 1, :-1].contiguous(),
            )
            output_logits = output.logits
            output_probs = torch.softmax(cast(torch.Tensor, output_logits), dim=-1)
            output_probs = output_probs[:, input_length - 1 :, :]
            output_sequences_new = output_sequences[i : i + 1, input_length:]
        output_probs_list.append(output_probs)
        output_sequences_list.append(output_sequences_new)

    return output_probs_list, output_sequences_list
