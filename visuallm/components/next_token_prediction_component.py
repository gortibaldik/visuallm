import logging

from visuallm.component_base import ComponentBase
from visuallm.components.generators.base import Generator, NextTokenPredictionInterface
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements import CollapsibleElement, HeadingElement, PlainTextElement
from visuallm.elements.barchart_element import BarChartElement, PieceInfo
from visuallm.elements.element_base import ElementBase


class GeneratorDoesNotSupportNextTokenPredictionError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "If you are using NextTokenPredictionComponent, the generator must be of type NextTokenPredictionInterface"
        )


class CreateTextToTokenizerOneStepIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "generator.create_text_to_tokenizer_one_step must not be None for NextTokenPredictionComponent"
        )


class CreateTextToTokenizerIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "generator.create_text_to_tokenizer must not be None for NextTokenPredictionComponent"
        )


class NextTokenPredictionComponent(
    ComponentBase, ModelSelectionMixin, DataPreparationMixin
):
    def __init__(
        self,
        title: str = "Next Token Prediction",
        generator: Generator | None = None,
        generator_choices: GENERATOR_CHOICES | None = None,
        dataset: DATASET_TYPE | None = None,
        dataset_choices: DATASETS_TYPE | None = None,
    ):
        """Enable user to step by step visualize what is the distribution of the
        next token during the generation of the sequence, and select the next token in the process.

        Args:
        ----
            title (str, optional): The title of the component, displayed at the top of the page,
                and in the tabs. Defaults to "Next Token Prediction".
            generator (Optional[Generator]): Generator used for predictions. Defaults to None.
            generator_choices (Optional[GENERATOR_CHOICES]): dictionary where key
                is the name of the generator and value is the generator. Defaults to None.
            dataset (Optional[DATASET_TYPE]): Dataset or a function that loads
                the dataset. Defaults to None.
            dataset_choices (Optional[DATASETS_TYPE]): Dictionary of datasets, or
                dictionary of functions that load the dataset. Defaults to None.
        """
        super().__init__(name="next_token_prediction", title=title)
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
            self,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        token_probs_display_elements = self.init_token_probs_display_elements()
        input_display_elements = self.init_model_input_display_elements()
        expected_output_elements = self.init_expected_output_display_elements()
        self._received_tokens: list[str] = []

        self.add_element(self.main_heading_element)

        collapsible_element = CollapsibleElement(title="Configuration")
        collapsible_element.add_subelements(self.dataset_choice_elements)
        collapsible_element.add_subelements(self.generator_selection_elements)
        self.add_element(collapsible_element)

        collapsible_element = CollapsibleElement(
            title="Inputs to Model", is_collapsed=False
        )
        collapsible_element.add_subelements(input_display_elements)
        self.add_element(collapsible_element)
        self.add_elements(expected_output_elements)
        self.add_elements(token_probs_display_elements)

    def __post_init__(self, *args, **kwargs):
        self.on_dataset_change_callback()

    def init_token_probs_display_elements(self) -> list[ElementBase]:
        """Init all the elements that display the next token predictions.

        Returns
        -------
            List[ElementBase]: list of elements that display the model's next token predictions.
        """
        self.token_probs_heading_element = PlainTextElement(
            content="Next Token Probabilities:", is_heading=True
        )
        self.token_probs_element = BarChartElement(
            processing_callback=self.on_next_token_selected,
        )
        return [self.token_probs_heading_element, self.token_probs_element]

    def init_model_input_display_elements(self) -> list[ElementBase]:
        """Init all the elements that display the model input, and the dataset sample.

        THIS METHOD SHOULD BE SET UP BY THE USER.

        Returns
        -------
            List[ElementBase]: list of elements that display the model's input.
        """
        text_to_tokenizer_heading_element = HeadingElement("Text to Tokenizer")
        self.text_to_tokenizer_element = PlainTextElement()
        return [text_to_tokenizer_heading_element, self.text_to_tokenizer_element]

    def init_expected_output_display_elements(self) -> list[ElementBase]:
        """Init all the elements that display the expected output."""
        expected_output_heading_element = HeadingElement("Expected Output")
        self.expected_output_element = PlainTextElement()
        return [expected_output_heading_element, self.expected_output_element]

    def update_model_input_display_on_sample_change(self):
        """After the sample change, self.loaded_sample holds the selected dataset sample.
        In this method the elements that display the model's input elements should be updated
        according to the self.loaded_sample.
        """
        if self.generator.create_text_to_tokenizer is None:
            raise CreateTextToTokenizerIsNoneError()
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(self.loaded_sample)
        )
        self._received_tokens = []

    def update_expected_output_display_on_sample_change(self):
        """After the sample change, self.loaded_sample holds the selected dataset sample.
        In this method the elements that display the expected output elements should be
        updated according to the self.loaded_sample
        """
        if self.generator.retrieve_target_str is None:
            raise ValueError(
                "Retrieve_target_str is None, cannot use generator for NextTokenPredictionComponent"
            )

        self.expected_output_element.content = self.generator.retrieve_target_str(
            self.loaded_sample
        )

    def update_model_input_display_on_selected_token(self):
        """After the next token to generate is selected, the model's input elements should be updated
        to reflect this change.

        You should base call this method with super() if you override it.

        Args:
        ----
            detokenized_token (str): the latest selected token
        """
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise GeneratorDoesNotSupportNextTokenPredictionError()
        if self.generator.create_text_to_tokenizer_one_step is None:
            raise CreateTextToTokenizerOneStepIsNoneError()
        text_to_tokenizer = self.generator.create_text_to_tokenizer_one_step(
            self.loaded_sample, self._received_tokens
        )
        self.text_to_tokenizer_element.content = text_to_tokenizer

    def run_generation_one_step(self) -> None:
        """Run one step of the generation and populates the token probabilities component
        with the next token probabilities.
        """
        text_to_tokenizer = self.text_to_tokenizer_element.content
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise GeneratorDoesNotSupportNextTokenPredictionError()
        n_largest_probs_tokens = self.generator.one_step_prediction(text_to_tokenizer)

        piece_infos: list[PieceInfo] = []
        for prob, token in n_largest_probs_tokens:
            piece_infos.append(
                PieceInfo(
                    pieceTitle=token,
                    barHeights=[prob],
                    barAnnotations=[f"{prob:.3f}%"],
                    barNames=[""],
                )
            )
        self.token_probs_element.set_piece_infos(piece_infos)

    def on_next_token_selected(self):
        """Callback that is called when the user selects next token in the frontend. Basically
        this callback changes the model's input according to the selected token, runs one step
        of the generation process, and populates the next token probabilities.
        """
        token = self.token_probs_element.selected
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise GeneratorDoesNotSupportNextTokenPredictionError()
        detokenized_token = self.generator.convert_token_to_string(token)
        self._received_tokens.append(detokenized_token)
        self.update_model_input_display_on_selected_token()
        self.run_generation_one_step()

    def after_on_dataset_change_callback(self):
        self.update_model_input_display_on_sample_change()
        self.update_expected_output_display_on_sample_change()
        self.run_generation_one_step()

    def after_on_generator_change_callback(self):
        # a new dataset sample is loaded which forces the prediction of the next step
        self.force_set_dataset_selector_updated()
        self.on_dataset_change_callback()

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

            if not isinstance(_generator, NextTokenPredictionInterface):
                raise GeneratorDoesNotSupportNextTokenPredictionError()
            if _generator.create_text_to_tokenizer_one_step is None:
                raise CreateTextToTokenizerOneStepIsNoneError()
            if _generator.create_text_to_tokenizer is None:
                raise CreateTextToTokenizerIsNoneError()
