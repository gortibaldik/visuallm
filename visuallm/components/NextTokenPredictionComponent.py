from heapq import nlargest
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from numpy.typing import NDArray
from transformers import PreTrainedModel, PreTrainedTokenizer
from transformers.tokenization_utils import BatchEncoding

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
from visuallm.elements.barchart_element import BarChartElement, PieceInfo
from visuallm.elements.element_base import ElementBase
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
        """This component enables you to step by step visualize what is the distribution of the
        next token during the generation of the sequence, and select the next token in the process.

        Args:
            title (str, optional): The title of the component, displayed at the top of the page,
                and in the tabs. Defaults to "Next Token Prediction".
            model (Optional[PreTrainedModel], optional): Huggingface model. Defaults to None.
            tokenizer (Optional[PreTrainedTokenizer], optional): Huggingface tokenizer. Defaults to None.
            model_tokenizer_choices (Optional[MODEL_TOKENIZER_CHOICES], optional): dictionary where key
                is the name of the tuple and value is tuple of tokenizer and model. Defaults to None.
            dataset (Optional[DATASET_TYPE], optional): Dataset or a function that loads
                the dataset. Defaults to None.
            dataset_choices (Optional[DATASETS_TYPE], optional): Dictionary of datasets, or
                dictionary of functions that load the dataset. Defaults to None.
            n_largest_tokens_to_return (int, optional): The vocabulary is large and it is not feasible to
                display all the possibilities, hence this allows you to choose only the tokens that have
                the largest probability assigned by the language model. Defaults to 10.
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
            self,
            dataset=dataset,
            dataset_choices=dataset_choices,
        )
        token_probs_display_elements = self.init_token_probs_display_elements()
        input_display_elements = self.init_model_input_display_elements()
        self._n_largest_tokens_to_return = n_largest_tokens_to_return
        self._init_word_vocab()

        super().__init__(
            name="next_token_prediction",
            title=title,
            elements=[
                self.main_heading_element,
                *self.dataset_elements,
                *self.model_elements,
                *input_display_elements,
                *token_probs_display_elements,
            ],
        )

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
        self.input_display = PlainTextElement()
        return [self.input_display]

    def update_model_input_display_on_sample_change(self):
        """
        After the sample change, self.loaded_sample holds the selected dataset sample.
        In this method the elements that display the model's input elements should be updated
        according to the self.loaded_sample.

        THIS METHOD SHOULD BE SET UP BY THE USER.
        """
        self.input_display.content = self.loaded_sample

    def update_model_input_display_on_selected_token(self, detokenized_token: str):
        """
        After the next token to generate is selected, the model's input elements should be updated
        to reflect this change.

        THIS METHOD SHOULD BE SET UP BY THE USER

        Args:
            detokenized_token (str): the latest selected token
        """
        self.input_display.content += detokenized_token

    def create_model_inputs(self) -> Union[Dict[str, Any], BatchEncoding]:
        """
        Create the inputs that will be put into the model. The model
        will be called as `model(**model_inputs)`.
        """
        model_inputs = self._tokenizer(self.input_display.content, return_tensors="pt")
        return model_inputs

    def _one_step_prediction(self) -> NDArray:
        """Pass the model inputs created by self.create_model_inputs through the data and
        return the numpy array with the probabilities of the next token.

        Returns:
            np.NDArray: probabilities of the next token.
        """
        model_inputs = self.create_model_inputs()
        with torch.no_grad():
            probs: torch.Tensor = self._model(**model_inputs).logits
            probs = torch.softmax(probs, dim=-1)
        np_probs: NDArray = probs[0, -1, :].numpy()
        return np_probs

    def _init_word_vocab(self):
        """Populate self._word_vocab, which is used to pair the array of the probabilities to
        the corresponding tokens.
        """
        vocab_size = len(self._tokenizer.get_vocab())
        self._word_vocab = [""] * vocab_size
        for str_val, int_val in self._tokenizer.get_vocab().items():
            self._word_vocab[int_val] = str_val

    def _get_n_largest_tokens_and_probs(
        self, probs: NDArray
    ) -> List[Tuple[float, str]]:
        """Get the self._n_largest_tokens_to_return largest probabilities from the probs array,
        and pair them with the corresponding str tokens.

        Args:
            probs (NDArray): array with probabilities of tokens assigned by the language model.

        Returns:
            List[Tuple[float, str]]: list of tuples of the token's probability and the corresponding
                token
        """
        if probs.shape[0] != len(self._word_vocab):
            raise RuntimeError("Word vocab is populated with wrong data!")

        return nlargest(
            n=self._n_largest_tokens_to_return,
            iterable=zip(map(lambda x: float(x) * 100, probs), self._word_vocab),
            key=lambda x: x[0],
        )

    def run_generation_one_step(self):
        """
        This method runs one step of the generation and populates the token probabilities component
        with the next token probabilities.
        """
        probs = self._one_step_prediction()
        n_largest_probs_tokens = self._get_n_largest_tokens_and_probs(probs)

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
        detokenized_token = self._tokenizer.convert_tokens_to_string([token])
        self.update_model_input_display_on_selected_token(detokenized_token)
        self.run_generation_one_step()

    def on_sample_change_callback(self):
        self.update_model_input_display_on_sample_change()
        self.run_generation_one_step()

    def on_model_change_callback(self):
        self._init_word_vocab()
        # a new dataset sample is loaded which forces the prediction of the next step
        self.force_set_dataset_selector_updated()
        self.dataset_callback()
