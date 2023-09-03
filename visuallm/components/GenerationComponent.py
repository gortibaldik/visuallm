from typing import Dict, List, Optional, cast

import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from transformers.generation.utils import GenerateOutput

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
    GeneratedTextMetric,
    MetricsMixin,
    ProbsMetric,
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
        metrics_on_generated_text: Dict[str, GeneratedTextMetric] = {},
        metrics_on_probs: Dict[str, ProbsMetric] = {},
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
        selectors: SELECTORS_TYPE = {},
    ):
        """This component provides generation capabilities. The user provides model, tokenizer
        and dataset, and this component displays all the elements needed to select element of the
        dataset, select generation parameters, display dataset element, model generations and the
        computed metrics.

        Args:
            title (str, optional): The title of the component. Defaults to "Interactive Generation".
            model (Optional[PreTrainedModel], optional): Huggingface model. Defaults to None.
            tokenizer (Optional[PreTrainedTokenizer], optional): Huggingface tokenizer. Defaults to None.
            model_tokenizer_choices (Optional[MODEL_TOKENIZER_CHOICES], optional): dictionary where key
                is the name of the tuple and value is tuple of tokenizer and model. Defaults to None.
            metrics_on_generated_text (Dict[str, GeneratedTextMetric], optional):
                Metrics which are computed on pairs of strings. Defaults to {}.
            metrics_on_probs (Dict[str, ProbsMetric], optional):
                Metrics which are computed on the probabilities of generations. Defaults to {}.
            dataset (Optional[DATASET_TYPE], optional): Dataset or a function that loads
                the dataset. Defaults to None.
            dataset_choices (Optional[DATASETS_TYPE], optional): Dictionary of datasets, or
                dictionary of functions that load the dataset. Defaults to None.
            selectors (SELECTORS_TYPE): dictionary of all the selectors which should
                be displayed on the frontend.
        """
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        ModelSelectionMixin.__init__(
            self,
            model_tokenizer_choices=model_tokenizer_choices,
            model=model,
            tokenizer=tokenizer,
        )
        DataPreparationMixin.__init__(
            self, dataset=dataset, dataset_choices=dataset_choices
        )
        GenerationSelectorsMixin.__init__(self, selectors=selectors)
        MetricsMixin.__init__(
            self,
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
                *self.metrics_selection_elements,
                *input_display_elements,
                *self.metrics_display_elements,
            ],
        )

    def init_model_input_display(self) -> List[ElementBase]:
        """Init elements that should display the dataset sample.

        Returns:
            List[ElementBase]: list of elements, it will be
                registered in the same order on the page.
        """
        self.input_display = PlainTextElement()
        return [self.input_display]

    def update_model_input_display(self):
        """Update the elements that display the dataset sample.

        This method is called each time a new dataset sample is loaded,
        and the loaded dataset sample is stored in `self.loaded_sample`
        """
        self.input_display.content = self.loaded_sample

    def create_model_inputs(self):
        """Create inputs for the model, which will be put in the huggingface
        model generate.

        Returns:
            Mapping[str, Tensor]: inputs to the model.generate
        """
        context = self.input_display.content
        model_inputs = self._tokenizer(context, return_tensors="pt")
        return model_inputs

    def create_target_encoding(self):
        """Create encoding of the target by the tokenizer.

        Returns:
            torch.Tensor: encoding of the target
        """
        context = self.input_display.content
        target = context + self.get_target_str()
        model_inputs = self._tokenizer(target, return_tensors="pt")
        return model_inputs.input_ids

    def get_target_str(self) -> str:
        """Get string that would be used for the computation of generation metrics."""
        return ""

    def update_generated_output_display(self):
        """Generate outputs with the model, measure probabilities, compute all the
        metrics and update metrics display elements."""
        model_inputs = self.create_model_inputs()
        output = generate_output(
            model_inputs,
            tokenizer=self._tokenizer,
            model=self._model,
            **self.selected_generation_parameters,
        )
        input_length = model_inputs.input_ids.size(1)
        decoded = decode_output(self._tokenizer, input_length, output)

        # compute mterics on generated
        probs, output_sequences = measure_output_probability(
            self._model, output.sequences, input_length
        )
        self.compute_n_display_metrics_on_predicted(
            decoded,
            self.get_target_str(),
            probs,
            output_sequences,
        )

        # compute scores on target
        probs, output_sequences = measure_output_probability(
            self._model, self.create_target_encoding(), input_length
        )
        self.compute_n_display_metrics_on_target(
            self.get_target_str(), probs, output_sequences
        )

    def on_model_change_callback(self):
        self.force_set_dataset_selector_updated()
        self.dataset_callback()

    def on_sample_change_callback(self):
        self.update_model_input_display()
        self.update_generated_output_display()

    def on_generation_changed_callback(self):
        return self.on_sample_change_callback()

    def metrics_processing_callback(self):
        return self.on_sample_change_callback()


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
    input_length: int,
    output: GenerateOutput,
):
    """Decode generated output and remove the input part from it.

    Args:
        tokenizer (PreTrainedTokenizer): tokenizer to use for decoding output
        input_length (int): length of input (we would remove the first part
            of the generated sequences, so that only the part that the model
            generated is returned)
        output (GenerateOutput): the output from huggingface model.generate

    Returns:
        List[str]: list of generated outputs from the model (only the generated part
            is returned, the input part is removed)
    """
    detokenized_outputs = tokenizer.batch_decode(
        output.sequences[:, input_length:],
        skip_special_tokens=True,
    )

    return detokenized_outputs


def measure_output_probability(
    model: PreTrainedModel,
    sequences: torch.Tensor,
    input_length: int,
):
    """
    At first model is used to generate tokens. Then we want to compute probabilities of
    individual tokens. While this method is really suboptimal, it is quite robust.

    Sequences is a tensor of shape (NUMBER_OF_GENERATIONS, LONGEST_GENERATION_LEN).
    Args:
        model (PreTrainedModel): the model with which to compute probabilities of tokens
        sequences (Tensor): sequences of ids to predict probabilities on
        input_length (int): length of the

    Returns:
        List[torch.Tensor], List[torch.Tensor]: assigned probabilities, only generated ids tensor
    """
    probabilities: List[torch.Tensor] = []
    output_sequences_list: List[torch.Tensor] = []
    for i in range(sequences.size(0)):
        with torch.no_grad():
            # TODO: here I should somehow treat generations of different lengths
            output = model(
                sequences[i : i + 1, :-1].contiguous(),
            )
            logits = output.logits
            probs = torch.softmax(cast(torch.Tensor, logits), dim=-1)
            probs = probs[:, input_length - 1 :, :]
            predicted_token_ids = sequences[i : i + 1, input_length:]
        probabilities.append(probs)
        output_sequences_list.append(predicted_token_ids)

    return probabilities, output_sequences_list
