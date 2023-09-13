import copy
import os
from abc import ABC, abstractmethod
from heapq import nlargest
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union, cast

import nltk
import openai
import torch
from numpy.typing import NDArray
from transformers import PreTrainedModel, PreTrainedTokenizer, PreTrainedTokenizerFast
from transformers.generation.utils import GenerateOutput


class CreateTextToTokenizer(Protocol):
    def __call__(self, loaded_sample: Any, target: Optional[Any] = None) -> Any:
        ...


class Generator(ABC):
    create_text_to_tokenizer: CreateTextToTokenizer

    @property
    def supports_next_token_prediction(self):
        return False

    @abstractmethod
    def generate_output(self, text_to_tokenizer: str, **kwargs) -> Dict:
        ...


TOKENIZER_TYPE = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]


class NextTokenPredictionInterface(ABC):
    """
    A class implementing this interface provides the ability to go over the
    generation in a token by token manner.
    """

    create_text_to_tokenizer_one_step: Callable[[Any, List[str]], str]

    @abstractmethod
    def one_step_prediction(self, text_to_tokenizer: str) -> List[Tuple[float, str]]:
        ...

    @abstractmethod
    def convert_token_to_string(self, token: str) -> str:
        ...

    @abstractmethod
    def init_word_vocab(self) -> List[str]:
        ...

    @property
    def supports_next_token_prediction(self):
        return True


class OutputProbabilityInterface(ABC):
    """
    A class implementing this interface provides `measure_output_probability` method
    thanks to which one can measure the probability of generated tokens.
    """

    @abstractmethod
    def measure_output_probability(
        self, texts: List[str], input_length: int
    ) -> Tuple[Any, Any]:
        """
        Measure the probabilities of individual tokens.

        Args:
            texts (List[str]): the generated sequences
            input_length (int): the length of tokenized input (only tokens after that are used for the
                probability computation)

        Returns:
            List[torch.Tensor], List[torch.Tensor]: assigned probabilities, generated_ids tensor
        """
        ...


class HuggingFaceGenerator(
    OutputProbabilityInterface, NextTokenPredictionInterface, Generator
):
    """Generator that generates using HuggingFace models and tokenizers."""

    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: TOKENIZER_TYPE,
        create_text_to_tokenizer: CreateTextToTokenizer,
        create_text_to_tokenizer_one_step: Callable[[Any, List[str]], str],
        n_largest_tokens_to_return: int = 10,
    ):
        self._model = model
        self._tokenizer = tokenizer
        self.create_text_to_tokenizer = create_text_to_tokenizer
        self.create_text_to_tokenizer_one_step = create_text_to_tokenizer_one_step
        self._n_largest_tokens_to_return = n_largest_tokens_to_return
        self.init_word_vocab()

    def generate_output(self, text_to_tokenizer: str, **kwargs):
        """Run model_inputs through self._model.generate"""

        model_inputs = self._tokenizer(text_to_tokenizer, return_tensors="pt")
        if "pad_token_id" not in kwargs:
            kwargs["pad_token_id"] = self._tokenizer.eos_token_id

        if "max_new_tokens" not in kwargs:
            kwargs["max_new_tokens"] = 40

        # generate with loaded settings
        output = self._model.generate(
            **model_inputs,
            output_scores=True,
            return_dict_in_generate=True,
            **kwargs,
        )
        output = cast(GenerateOutput, output)
        input_length: int = model_inputs.input_ids.size(1)

        decoded_outputs = self.decode_output(output, input_length)

        return dict(
            output=output, decoded_outputs=decoded_outputs, input_length=input_length
        )

    def decode_output(
        self,
        output: GenerateOutput,
        input_length: int,
    ):
        """Decode generated output and remove the input part from it.

        Args:
            output (GenerateOutput): the output from huggingface model.generate
            input_length (int): length of input (we would remove the first part
                of the generated sequences, so that only the part that the model
                generated is returned)

        Returns:
            List[str]: list of generated outputs from the model (only the generated part
                is returned, the input part is removed)
        """
        detokenized_outputs = self._tokenizer.batch_decode(
            output.sequences[:, input_length:],
            skip_special_tokens=True,
        )

        return detokenized_outputs

    def one_step_prediction(self, text_to_tokenizer: str) -> List[Tuple[float, str]]:
        """Pass the model inputs created by self.create_model_inputs through the data and
        return the numpy array with the probabilities of the next token.

        Returns:
            np.NDArray: probabilities of the next token of shape (vocab_size, )
        """
        model_inputs = self._tokenizer(text_to_tokenizer, return_tensors="pt")
        with torch.no_grad():
            probs: torch.Tensor = self._model(**model_inputs).logits
            probs = torch.softmax(probs, dim=-1)
        np_probs: NDArray = probs[0, -1, :].numpy()

        return self.get_n_largest_tokens_and_probs(np_probs)

    def convert_token_to_string(self, token: str):
        return self._tokenizer.convert_tokens_to_string([token])

    def init_word_vocab(self) -> None:
        vocab_size = len(self._tokenizer.get_vocab())
        word_vocab = [""] * vocab_size
        for str_val, int_val in self._tokenizer.get_vocab().items():
            word_vocab[int_val] = str_val
        self.word_vocab = word_vocab

    def measure_output_probability(self, texts: List[str], input_length: int):
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
        for text in texts:
            with torch.inference_mode():
                sequence = self._tokenizer(text, return_tensors="pt")
                output = self._model(**sequence)
                logits = cast(torch.Tensor, output.logits)
                probs = torch.softmax(logits, dim=-1)
                probs = probs[:, input_length - 1 : -1, :]
                predicted_token_ids = sequence.input_ids[0, input_length:]
            probabilities.append(probs)
            output_sequences_list.append(predicted_token_ids)

        return probabilities, output_sequences_list

    def get_n_largest_tokens_and_probs(self, probs: NDArray) -> List[Tuple[float, str]]:
        """Get the self._n_largest_tokens_to_return largest probabilities from the probs array,
        and pair them with the corresponding str tokens.

        Args:
            probs (NDArray): array with probabilities of tokens assigned by the language model. Shape (vocab_size,)

        Returns:
            List[Tuple[float, str]]: list of tuples of the token's probability and the corresponding
                token
        """
        if probs.shape[0] != len(self.word_vocab):
            raise RuntimeError("Word vocab is populated with wrong data!")

        return nlargest(
            n=self._n_largest_tokens_to_return,
            iterable=zip(map(lambda x: float(x) * 100, probs), self.word_vocab),
            key=lambda x: x[0],
        )


class OpenAIGenerator(Generator):
    def __init__(self, create_text_to_tokenizer: CreateTextToTokenizer):
        self._api_key = os.getenv("OPENAI_API_KEY")
        if self._api_key is None:
            raise ValueError("OPENAI_API_KEY not set!")

        self.create_text_to_tokenizer = create_text_to_tokenizer
        openai.api_key = self._api_key

    def generate_output(self, text_to_tokenizer: Dict, **kwargs) -> Dict:
        params = copy.deepcopy(text_to_tokenizer)
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "num_return_sequences" in kwargs:
            params["n"] = kwargs["num_return_sequences"]
        if "max_new_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_new_tokens"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        response = openai.ChatCompletion.create(**params)
        return dict(
            decoded_outputs=[choice["message"]["content"] for choice in response["choices"]]  # type: ignore
        )


forms = {
    "am": "are",
    "Am": "Are",
    "are": "am",
    "Are": "Am",
    "i": "you",
    "I": "You",
    "you": "i",
    "You": "I",
    "my": "your",
    "My": "Your",
    "your": "my",
    "Your": "My",
    "yours": "mine",
    "Yours": "Mine",
    "Mine": "Yours",
    "mine": "yours",
    "me": "you",
    "Me": "You",
}


def switch_persona_from_first_to_second_word(word: str):
    return forms.get(word, word)


def switch_persona_from_first_to_second_sentence(sentence: str):
    return " ".join(
        [
            switch_persona_from_first_to_second_word(word)
            for word in nltk.wordpunct_tokenize(sentence)
        ]
    )
