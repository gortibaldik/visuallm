from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, Union

from transformers import PreTrainedModel, PreTrainedTokenizer, PreTrainedTokenizerFast

from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.selector_elements import ButtonElement, ChoicesSubElement

if TYPE_CHECKING:
    from visuallm.elements import ElementBase

TOKENIZER_TYPE = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]

TOKENIZER_MODEL_TUPLE = Tuple[TOKENIZER_TYPE, PreTrainedModel]
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
        model: Optional[PreTrainedModel] = None,
        tokenizer: Optional[TOKENIZER_TYPE] = None,
        model_tokenizer_choices: Optional[MODEL_TOKENIZER_CHOICES] = None,
        keep_models_in_memory: bool = True,
    ):
        """This mixin implements model handling server methods. If only the
        model and the tokenizer is provided, the mixin just makes `self.model` and
        `self.tokenizer` properties available. If the `model_tokenizer_choices` is available
        then the mixin creates frontend elements which let the user select the model and
        the tokenizer.

        Warning:
            You should either provide the model and the tokenizer or model_tokenizer_choices,
            not both at once.

        Args:
            model (Optional[PreTrainedModel], optional): Huggingface model. Defaults to None.
            tokenizer (Optional[PreTrainedTokenizer], optional): Huggingface tokenizer. Defaults to None.
            model_tokenizer_choices (Optional[MODEL_TOKENIZER_CHOICES], optional): dictionary where key
                is the name of the tuple and value is tuple of tokenizer and model. Defaults to None.
            keep_models_in_memory (bool, optional): Whether to load the tokenizer and model to cache, so that
                when a new tokenizer and model is loaded, the old one remains in memory. It makes switching
                between different tokenizers and models faster. Defaults to True.
        """
        if model is None and (
            model_tokenizer_choices is None or len(model_tokenizer_choices) == 0
        ):
            raise ValueError(
                "You have to provide either model and tokenizer or a not "
                + "empty model_tokenizer_choices dictionary"
            )

        if model is None and tokenizer is None:
            assert model_tokenizer_choices is not None
            self._model_choices = model_tokenizer_choices
        elif model is None or tokenizer is None:
            raise ValueError(
                "If you provide the model, you should also provide the tokenizer."
            )
        else:
            if model_tokenizer_choices is not None:
                raise ValueError(
                    "If model, tokenizer and model_tokenizer_choices is all "
                    + "not None, the library cannot decide which should be "
                    + "selected."
                )
            self._model_choices = None
            self._model, self._tokenizer = model, tokenizer

        self._cache: Optional[Dict[str, TOKENIZER_MODEL_TUPLE]] = None
        if keep_models_in_memory:
            self._cache = {}
        self.initialize_model_elements()

        if model_tokenizer_choices is not None:
            self._tokenizer, self._model = self.load_model(
                model_tokenizer_choices[self.model_selector_element.selected]
            )

    def load_model(
        self,
        model_constructor: Union[
            TOKENIZER_MODEL_TUPLE,
            Callable[[], TOKENIZER_MODEL_TUPLE],
        ],
    ):
        """Load the model and the tokenizer using the provided `model_constructor`

        Args:
            model_constructor (Union[ TOKENIZER_MODEL_TUPLE, Callable[[], TOKENIZER_MODEL_TUPLE], ]): either
                the model and the tokenizer tuple or a function that loads the model and
                the tokenizer tuple.

        Returns:
            TOKENIZER_MODEL_TUPLE: loaded tokenizer and model
        """
        if isinstance(model_constructor, tuple):
            return model_constructor
        else:
            return model_constructor()

    def load_cached_model(
        self,
        model_constructor: Callable[[], TOKENIZER_MODEL_TUPLE],
        name: Optional[str] = None,
    ) -> None:
        """The behavior of this function depends on whether the caching is set or unset.

        If set, the function at first checks whether the tokenizer and the model with `name`
        is already in the cache and skips the loading and returns the cached value, or if it
        isn't then it loads the tokenizer and the model, and stores it into the cache and
        returns.

        If unset, the function just loads the tokenizer and the model and returns it.

        Important:
            The loaded tokenizer is stored in the property: `self.tokenizer` and the loaded
            model is stored in the property: `self.model`

        Args:
            name (str): name of the tokenizer and the model, the tuple will be stored in the
                cache under this name.
            model_constructor (Callable[[], TOKENIZER_MODEL_TUPLE]): function that loads the
                tokenizer and the model.
        """
        if self._cache is not None and name in self._cache:
            self._tokenizer, self._model = self._cache[name]
        self._tokenizer, self._model = model_constructor()
        if self._cache is not None and name is not None:
            self._cache[name] = (self._tokenizer, self._model)

    def initialize_model_elements(self):
        """Initializes a heading with text "Model Settings" and a selector
        element, which contains:
        - selector for specific tokenizer and model if multiple tokenizers and models
            are provided
        """
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
    def model_selection_elements(self) -> List[ElementBase]:
        """All the model selection elements that should be displayed on the frontend."""
        if self._model_choices is None:
            return []
        return [self.model_selector_heading, self.button_element]

    def on_model_change_callback(self):
        """What to do after the new model and tokenizer is loaded."""
        pass

    def model_callback(self):
        """
        This method is called each time when a request from frontend comes to load
        a different tokenizer and model.
        """
        assert self._model is not None
        if self._model_choices is None:
            return
        if self.model_selector_element.updated:
            name = self.model_selector_element.selected
            model_tokenizer = self._model_choices[name]
            self.load_cached_model(lambda: self.load_model(model_tokenizer), name)
            self.on_model_change_callback()
