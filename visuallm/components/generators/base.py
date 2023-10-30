import dataclasses
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Protocol


class CreateTextToTokenizer(Protocol):

    """The library enforces the following flow:
    1. a text to the tokenizer is created from the loaded sample and returned (handled by this method)
    2. the text to the tokenizer is passed to the generator to tokenize and create a generation

    This way we can display the text to the tokenizer in the frontend and check whether we aren't sending
    garbage to the model.
    """

    def __call__(self, loaded_sample: dict[str, Any], target: Any | None = None) -> str:
        ...


class RetrieveTargetStr(Protocol):
    def __call__(self, loaded_sample: Any) -> str:
        ...


@dataclasses.dataclass
class GeneratedOutput:
    decoded_outputs: list[str]
    """Human readable outputs of the generator (generated texts)"""
    input_length: int | None = None
    """Length of the tokenized inputs"""


class Generator(ABC):
    create_text_to_tokenizer: CreateTextToTokenizer
    """The library enforces the following flow:
    1. a text to the tokenizer is created from the loaded sample and returned (handled by this method)
    2. the text to the tokenizer is passed to the generator to tokenize and create a generation

    This way we can display the text to the tokenizer in the frontend and check whether we aren't sending
    garbage to the model.
    """
    retrieve_target_str: RetrieveTargetStr

    @property
    def supports_next_token_prediction(self):
        """Whether the generator supports NextTokenPrediction (can be plugged into the
        NextTokenPredictionComponent, e.g. it can return probabilities of tokens and
        step over the token prediction).
        """
        return False

    @abstractmethod
    def generate_output(self, text_to_tokenizer: str, **kwargs) -> GeneratedOutput:
        ...


class NextTokenPredictionInterface(ABC):

    """A class implementing this interface provides the ability to go over the
    generation in a token by token manner.
    """

    create_text_to_tokenizer_one_step: Callable[[Any, list[str]], str]

    @abstractmethod
    def one_step_prediction(self, text_to_tokenizer: str) -> list[tuple[float, str]]:
        ...

    @abstractmethod
    def convert_token_to_string(self, token: str) -> str:
        ...

    @abstractmethod
    def init_word_vocab(self) -> list[str]:
        ...

    @property
    def supports_next_token_prediction(self):
        return True


class OutputProbabilityInterface(ABC):

    """A class implementing this interface provides `measure_output_probability` method
    thanks to which one can measure the probability of generated tokens.
    """

    @abstractmethod
    def measure_output_probability(
        self, texts: list[str], input_length: int
    ) -> tuple[Any, Any]:
        """Measure the probabilities of individual tokens.

        Args:
        ----
            texts (List[str]): the generated sequences
            input_length (int): the length of tokenized input (only tokens after that are used for the
                probability computation)

        Returns:
        -------
            List[torch.Tensor], List[torch.Tensor]: assigned probabilities, generated_ids tensor
        """
        ...