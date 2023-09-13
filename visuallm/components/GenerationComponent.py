from typing import Dict, List, Optional, cast

import torch
from transformers import PreTrainedModel
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
from visuallm.components.mixins.Generator import Generator, OutputProbabilityInterface
from visuallm.components.mixins.metrics_mixin import (
    GeneratedTextMetric,
    MetricsMixin,
    ProbsMetric,
)
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements import HeadingElement, PlainTextElement
from visuallm.elements.element_base import ElementBase


class GenerationComponent(
    ComponentBase,
    DataPreparationMixin,
    ModelSelectionMixin,
    GenerationSelectorsMixin,
    MetricsMixin,
):
    def __init__(
        self,
        title: str = "Interactive Generation",
        generator: Optional[Generator] = None,
        generator_choices: Optional[GENERATOR_CHOICES] = None,
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
            generator (Optional[Generator], optional): Generator. Defaults to None.
            generator_choices (Optional[GENERATOR_CHOICES], optional): dictionary where key
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
        super().__init__(name="interactive_generation", title=title)
        self.main_heading_element = PlainTextElement(
            is_heading=True, heading_level=2, content=title
        )
        ModelSelectionMixin.__init__(
            self,
            generator_choices=generator_choices,
            generator=generator,
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
        self.add_element(self.main_heading_element)
        self.add_elements(self.dataset_elements)
        self.add_elements(self.generator_selection_elements)
        self.add_elements(self.generation_elements)
        self.add_elements(self.metrics_selection_elements)
        self.add_elements(input_display_elements)
        self.add_elements(self.metrics_display_elements)

    def init_model_input_display(self) -> List[ElementBase]:
        """Init elements that should display the dataset sample.

        Returns:
            List[ElementBase]: list of elements, it will be
                registered in the same order on the page.
        """
        text_to_tokenizer_heading = HeadingElement("Text to Tokenizer")
        self.text_to_tokenizer_element = PlainTextElement()
        return [text_to_tokenizer_heading, self.text_to_tokenizer_element]

    def update_model_input_display(self):
        """Update the elements that display the dataset sample.

        This method is called each time a new dataset sample is loaded,
        and the loaded dataset sample is stored in `self.loaded_sample`
        """
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(self.loaded_sample)
        )

    def get_target_str(self) -> str:
        """Get string that would be used for the computation of generation metrics."""
        return ""

    def update_generated_output_display(self):
        """Generate outputs with the model, measure probabilities, compute all the
        metrics and update metrics display elements."""
        text_to_tokenizer = self.text_to_tokenizer_element.content
        output = self.generator.generate_output(
            text_to_tokenizer, **self.selected_generation_parameters
        )

        # compute metrics on generated
        probs, output_sequences = None, None

        if isinstance(self.generator, OutputProbabilityInterface):
            full_generated_texts = [
                self.generator.create_text_to_tokenizer(self.loaded_sample, generated)
                for generated in output["decoded_outputs"]
            ]
            probs, output_sequences = self.generator.measure_output_probability(
                full_generated_texts, output["input_length"]
            )
        else:
            probs = [None] * len(output["decoded_outputs"])
            output_sequences = probs

        self.compute_n_display_metrics_on_predicted(
            output["decoded_outputs"],
            self.get_target_str(),
            probs,
            output_sequences,
        )

        # compute scores on target
        if isinstance(self.generator, OutputProbabilityInterface):
            probs, output_sequences = self.generator.measure_output_probability(
                [
                    self.generator.create_text_to_tokenizer(
                        self.loaded_sample, self.get_target_str()
                    )
                ],
                output["input_length"],
            )
        else:
            probs, output_sequences = [None], [None]
        self.compute_n_display_metrics_on_target(
            self.get_target_str(),
            probs,
            output_sequences,
        )

    def after_on_generator_change_callback(self):
        self.force_set_dataset_selector_updated()
        self.on_dataset_change_callback()

    def after_on_dataset_change_callback(self):
        self.update_model_input_display()
        self.update_generated_output_display()

    def on_generation_changed_callback(self):
        return self.after_on_dataset_change_callback()

    def metrics_processing_callback(self):
        return self.after_on_dataset_change_callback()


def generate_output(
    model_inputs,
    *,
    tokenizer,
    model: PreTrainedModel,
    max_new_tokens: int = 40,
    **kwargs,
):
    """Returns generated indices and log probabilities of generated indices."""

    # generate with loaded settings
    output = model.generate(
        **model_inputs,
        pad_token_id=tokenizer.eos_token_id,
        output_scores=True,
        return_dict_in_generate=True,
        max_new_tokens=max_new_tokens,
        **kwargs,
    )
    output = cast(GenerateOutput, output)

    return output


def decode_output(
    tokenizer,
    input_length: int,
    output: GenerateOutput,
):
    """Decode generated output and remove the input part from it.

    Args:
        tokenizer (TOKENIZER_TYPE): tokenizer to use for decoding output
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
        output: the result of self.generate_output

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
