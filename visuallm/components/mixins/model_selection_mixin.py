from typing import Callable, Dict, Optional, Tuple, Union

from transformers import PreTrainedModel, PreTrainedTokenizer

from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import ButtonElement, ChoicesSubElement

TOKENIZER_MODEL_TUPLE = Tuple[PreTrainedTokenizer, PreTrainedModel]
MODEL_TOKENIZER_CHOICES = Union[
    Dict[str, TOKENIZER_MODEL_TUPLE],
    Dict[
        str,
        Callable[[], TOKENIZER_MODEL_TUPLE],
    ],
]


class ModelSelectionMixin:
    def __init__(
        self,
        on_model_change_callback: Callable[[], None],
        model: Optional[PreTrainedModel] = None,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        model_tokenizer_choices: Optional[MODEL_TOKENIZER_CHOICES] = None,
        keep_models_in_memory: bool = True,
    ):
        if model is None and (
            model_tokenizer_choices is None or len(model_tokenizer_choices) == 0
        ):
            raise ValueError()

        if model is None or tokenizer is None:
            assert model_tokenizer_choices is not None
            self._model_choices = model_tokenizer_choices
        else:
            assert model_tokenizer_choices is None
            self._model_choices = None
            self._model, self._tokenizer = model, tokenizer

        self._cache: Optional[Dict[str, TOKENIZER_MODEL_TUPLE]] = None
        if keep_models_in_memory:
            self._cache = {}
        self._on_model_change_callback = on_model_change_callback
        self.initialize_model_elements()

        if model_tokenizer_choices is not None:
            self._tokenizer, self._model = self.load_model(
                model_tokenizer_choices[self.model_selector_element.selected]
            )

    def load_model(
        self,
        value: Union[
            TOKENIZER_MODEL_TUPLE,
            Callable[[], TOKENIZER_MODEL_TUPLE],
        ],
    ):
        if isinstance(value, tuple):
            return value
        else:
            return value()

    def initialize_model_elements(self):
        if self._model_choices is None:
            return

        self.model_selector_heading = PlainTextElement(
            content="Model Settings", is_heading=True
        )
        self.model_selector_element = ChoicesSubElement(
            list(self._model_choices), text="Select Model"
        )
        self.button_element = ButtonElement(
            processing_callback=self.model_callback,
            button_text="Send Model Configuration",
            subelements=[self.model_selector_element],
        )

    @property
    def model_elements(self):
        if self._model_choices is None:
            return []
        return [self.model_selector_heading, self.button_element]

    def model_callback(self):
        assert self._model is not None
        if self._model_choices is None:
            return
        if self.model_selector_element.updated:
            key = self.model_selector_element.selected
            if self._cache is not None and key in self._cache:
                self._tokenizer, self._model = self._cache[key]
            else:
                self._tokenizer, self._model = self.load_model(self._model_choices[key])
                if self._cache is not None:
                    self._cache[key] = (self._tokenizer, self._model)
            self._on_model_change_callback()
