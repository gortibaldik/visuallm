from typing import List, Optional

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.data_preparation_mixin import (
    DATASET_TYPE,
    DATASETS_TYPE,
    DataPreparationMixin,
)
from visuallm.components.mixins.Generator import Generator, NextTokenPredictionInterface
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements.barchart_element import BarChartElement, PieceInfo
from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement


class NextTokenPredictionComponent(
    ComponentBase, ModelSelectionMixin, DataPreparationMixin
):
    def __init__(
        self,
        title: str = "Next Token Prediction",
        generator: Optional[Generator] = None,
        generator_choices: Optional[GENERATOR_CHOICES] = None,
        dataset: Optional[DATASET_TYPE] = None,
        dataset_choices: Optional[DATASETS_TYPE] = None,
    ):
        """This component enables you to step by step visualize what is the distribution of the
        next token during the generation of the sequence, and select the next token in the process.

        Args:
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
        DataPreparationMixin.__init__(
            self,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        token_probs_display_elements = self.init_token_probs_display_elements()
        input_display_elements = self.init_model_input_display_elements()
        self._received_tokens: List[str] = []

        self.add_element(self.main_heading_element)
        self.add_elements(self.dataset_elements)
        self.add_elements(self.generator_selection_elements)
        self.add_elements(input_display_elements)
        self.add_elements(token_probs_display_elements)

    def __post_init__(self):
        pass

    def init_token_probs_display_elements(self) -> List[ElementBase]:
        """Init all the elements that display the next token predictions.

        Returns:
            List[ElementBase]: list of elements that display the model's next token predictions.
        """
        self.token_probs_heading_element = PlainTextElement(
            content="Next Token Probabilities:", is_heading=True
        )
        self.token_probs_element = BarChartElement(
            processing_callback=self.on_next_token_selected,
        )
        return [self.token_probs_heading_element, self.token_probs_element]

    def init_model_input_display_elements(self) -> List[ElementBase]:
        """
        Init all the elements that display the model input, and the dataset sample.

        THIS METHOD SHOULD BE SET UP BY THE USER.

        Returns:
            List[ElementBase]: list of elements that display the model's input.
        """
        self.text_to_tokenizer_element = PlainTextElement()
        return [self.text_to_tokenizer_element]

    def update_model_input_display_on_sample_change(self):
        """
        After the sample change, self.loaded_sample holds the selected dataset sample.
        In this method the elements that display the model's input elements should be updated
        according to the self.loaded_sample.
        """
        self.text_to_tokenizer_element.content = (
            self.generator.create_text_to_tokenizer(self.loaded_sample)
        )
        self._received_tokens = []

    def update_model_input_display_on_selected_token(self):
        """
        After the next token to generate is selected, the model's input elements should be updated
        to reflect this change.

        You should base call this method with super() if you override it.

        Args:
            detokenized_token (str): the latest selected token
        """
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise ValueError()
        text_to_tokenizer = self.generator.create_text_to_tokenizer_one_step(
            self.loaded_sample, self._received_tokens
        )
        self.text_to_tokenizer_element.content = text_to_tokenizer

    def run_generation_one_step(self):
        """
        This method runs one step of the generation and populates the token probabilities component
        with the next token probabilities.
        """
        text_to_tokenizer = self.text_to_tokenizer_element.content
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise ValueError()
        n_largest_probs_tokens = self.generator.one_step_prediction(text_to_tokenizer)

        piece_infos: List[PieceInfo] = []
        for prob, token in n_largest_probs_tokens:
            piece_infos.append(
                PieceInfo(
                    pieceTitle=token,
                    barHeights=[prob],
                    barAnnotations=["{:.3f}%".format(prob)],
                    barNames=[""],
                )
            )
        self.token_probs_element.set_piece_infos(piece_infos)

    def on_next_token_selected(self):
        """
        Callback that is called when the user selects next token in the frontend. Basically
        this callback changes the model's input according to the selected token, runs one step
        of the generation process, and populates the next token probabilities.
        """
        token = self.token_probs_element.selected
        if not isinstance(self.generator, NextTokenPredictionInterface):
            raise ValueError()
        detokenized_token = self.generator.convert_token_to_string(token)
        self._received_tokens.append(detokenized_token)
        self.update_model_input_display_on_selected_token()
        self.run_generation_one_step()

    def after_on_dataset_change_callback(self):
        self.update_model_input_display_on_sample_change()
        self.run_generation_one_step()

    def after_on_generator_change_callback(self):
        # a new dataset sample is loaded which forces the prediction of the next step
        self.force_set_dataset_selector_updated()
        self.on_dataset_change_callback()
