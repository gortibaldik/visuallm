import logging

from visuallm.component_base import ComponentBase
from visuallm.components.generators.base import Generator, OutputProbabilityInterface
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
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements import CollapsibleElement, HeadingElement, PlainTextElement
from visuallm.elements.element_base import ElementBase


class CreateTextToTokenizerIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "self.generator.create_text_to_tokenizer cannot be None in GenerationComponent"
        )


class RetrieveTargetStrIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Retrieve_target_str is None, generator cannot be used for GenerationComponent"
        )


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
        generator: Generator | None = None,
        generator_choices: GENERATOR_CHOICES | None = None,
        metrics_on_generated_text: dict[str, GeneratedTextMetric] | None = None,
        metrics_on_probs: dict[str, ProbsMetric] | None = None,
        dataset: DATASET_TYPE | None = None,
        dataset_choices: DATASETS_TYPE | None = None,
        selectors: SELECTORS_TYPE | None = None,
    ):
        """Provide generation capabilities. The user provides model, tokenizer
        and dataset, and this component displays all the elements needed to select element of the
        dataset, select generation parameters, display dataset element, model generations and the
        computed metrics.

        Args:
        ----
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
        self._check_generators(self.generator, generator_choices)
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
        collapsible_element = CollapsibleElement(title="Configuration")
        collapsible_element.add_subelements(self.dataset_choice_elements)
        collapsible_element.add_subelements(self.generator_selection_elements)
        collapsible_element.add_subelements(self.generation_elements)
        collapsible_element.add_subelements(self.metrics_selection_elements)
        self.add_element(collapsible_element)

        # naming everything the same because I lack originality
        collapsible_element = CollapsibleElement(
            title="Inputs to Model", is_collapsed=False
        )
        collapsible_element.add_subelements(input_display_elements)
        self.add_element(collapsible_element)
        self.add_elements(self.metrics_display_elements)

    def __post_init__(self, *args, **kwargs):
        self.on_dataset_change_callback()

    def init_model_input_display(self) -> list[ElementBase]:
        """Init elements that should display the dataset sample.

        Returns
        -------
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
        if self.generator.create_text_to_tokenizer is None:
            raise CreateTextToTokenizerIsNoneError()
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(self.loaded_sample)
        )

    def update_generated_output_display(self):
        """Generate outputs with the model, measure probabilities, compute all the
        metrics and update metrics display elements.
        """
        if self.generator.retrieve_target_str is None:
            raise RetrieveTargetStrIsNoneError()
        text_to_tokenizer = self.text_to_tokenizer_element.content
        output = self.generator.generate_output(
            text_to_tokenizer, **self.selected_generation_parameters
        )

        # compute metrics on generated
        probs, output_sequences = None, None

        if (
            isinstance(self.generator, OutputProbabilityInterface)
            and output.input_length is not None
        ):
            if self.generator.create_text_to_tokenizer is None:
                raise CreateTextToTokenizerIsNoneError()
            full_generated_texts = [
                self.generator.create_text_to_tokenizer(self.loaded_sample, generated)
                for generated in output.decoded_outputs
            ]
            probs, output_sequences = self.generator.measure_output_probability(
                full_generated_texts, output.input_length
            )
        else:
            probs = [None] * len(output.decoded_outputs)
            output_sequences = probs

        self.compute_n_display_metrics_on_predicted(
            output.decoded_outputs,
            self.generator.retrieve_target_str(self.loaded_sample),
            probs,
            output_sequences,
        )

        # compute scores on target
        if (
            isinstance(self.generator, OutputProbabilityInterface)
            and output.input_length is not None
        ):
            if self.generator.create_text_to_tokenizer is None:
                raise CreateTextToTokenizerIsNoneError()
            probs, output_sequences = self.generator.measure_output_probability(
                [
                    self.generator.create_text_to_tokenizer(
                        self.loaded_sample,
                        self.generator.retrieve_target_str(self.loaded_sample),
                    )
                ],
                output.input_length,
            )
        else:
            probs, output_sequences = [None], [None]
        self.compute_n_display_metrics_on_target(
            self.generator.retrieve_target_str(self.loaded_sample),
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

    def _check_generators(
        self,
        generator: Generator | None,
        generator_choices: GENERATOR_CHOICES | None,
    ):
        if generator_choices is None:
            if generator is None:
                raise ValueError(
                    "Either generator_choices or generator should not be None"
                )
            generator_choices = {"default": generator}

        for _name, _generator in generator_choices.items():
            if callable(_generator):
                logging.info(f"Not checking generator '{_name}' because it is callable")
                continue
            if (
                isinstance(_generator, OutputProbabilityInterface)
                and _generator.create_text_to_tokenizer is None
            ):
                raise CreateTextToTokenizerIsNoneError()
            if _generator.retrieve_target_str is None:
                raise RetrieveTargetStrIsNoneError()
