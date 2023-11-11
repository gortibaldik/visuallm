from collections.abc import Callable
from heapq import nlargest
from typing import TYPE_CHECKING, Any, TypeAlias, cast

from transformers.generation.utils import GenerateOutput

from visuallm.components.generators.base import (
    CreateTextToTokenizer,
    CreateTextToTokenizerChat,
    GeneratedOutput,
    Generator,
    NextTokenPredictionInterface,
    OutputProbabilityInterface,
    RetrieveTargetStr,
)

try:
    import torch
    import transformers  # noqa: F401
except ImportError:
    _has_torch = False
else:
    _has_torch = True


if TYPE_CHECKING:
    from numpy.typing import NDArray
    from transformers import (
        PreTrainedModel,
        PreTrainedTokenizer,
        PreTrainedTokenizerFast,
    )

    TOKENIZER_TYPE: TypeAlias = PreTrainedTokenizer | PreTrainedTokenizerFast


class HuggingFaceGenerator(
    OutputProbabilityInterface, NextTokenPredictionInterface, Generator
):

    """Generator that generates using HuggingFace models and tokenizers."""

    def __init__(
        self,
        model: "PreTrainedModel",
        tokenizer: "TOKENIZER_TYPE",
        retrieve_target_str: RetrieveTargetStr,
        n_largest_tokens_to_return: int = 10,
        create_text_to_tokenizer: CreateTextToTokenizer | None = None,
        create_text_to_tokenizer_chat: CreateTextToTokenizerChat | None = None,
        create_text_to_tokenizer_one_step: Callable[[Any, list[str]], str]
        | None = None,
    ):
        if not _has_torch:
            raise RuntimeError(
                "Torch or HuggingFace Transformers isn't installed, HuggingFaceGenerator needs them."
            )
        self._model = model
        self._tokenizer = tokenizer
        self.create_text_to_tokenizer = create_text_to_tokenizer
        self.create_text_to_tokenizer_chat = create_text_to_tokenizer_chat
        self.create_text_to_tokenizer_one_step = create_text_to_tokenizer_one_step
        self.retrieve_target_str = retrieve_target_str
        self._n_largest_tokens_to_return = n_largest_tokens_to_return
        self.init_word_vocab()

    def generate_output(
        self, text_to_tokenizer: str, **generation_arguments: Any
    ) -> GeneratedOutput:
        """Run model_inputs through self._model.generate"""
        model_inputs = self._tokenizer(text_to_tokenizer, return_tensors="pt")
        if "pad_token_id" not in generation_arguments:
            generation_arguments["pad_token_id"] = self._tokenizer.eos_token_id

        if "max_new_tokens" not in generation_arguments:
            generation_arguments["max_new_tokens"] = 40

        # generate with loaded settings
        output = self._model.generate(
            **model_inputs,
            output_scores=True,
            return_dict_in_generate=True,
            **generation_arguments,
        )
        output = cast(GenerateOutput, output)
        input_length: int = model_inputs.input_ids.size(1)

        decoded_outputs = self.decode_output(output, input_length)

        return GeneratedOutput(
            decoded_outputs=decoded_outputs, input_length=input_length
        )

    def decode_output(
        self,
        output: GenerateOutput,
        input_length: int,
    ):
        """Decode generated output and remove the input part from it.

        Args:
        ----
            output (GenerateOutput): the output from huggingface model.generate
            input_length (int): length of input (we would remove the first part
                of the generated sequences, so that only the part that the model
                generated is returned)

        Returns:
        -------
            List[str]: list of generated outputs from the model (only the generated part
                is returned, the input part is removed)
        """
        detokenized_outputs = self._tokenizer.batch_decode(
            output.sequences[:, input_length:],
            skip_special_tokens=True,
        )

        return detokenized_outputs

    def one_step_prediction(self, text_to_tokenizer: str) -> list[tuple[float, str]]:
        """Pass the model inputs created by self.create_model_inputs through the data and
        return the numpy array with the probabilities of the next token.

        Returns
        -------
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

    def measure_output_probability(self, texts: list[str], input_length: int):
        """At first model is used to generate tokens. Then we want to compute probabilities of
        individual tokens. While this method is really suboptimal, it is quite robust.

        Sequences is a tensor of shape (NUMBER_OF_GENERATIONS, LONGEST_GENERATION_LEN).

        Args:
        ----
            texts (list[str]): TODO
            input_length (int): TODO

        Returns:
        -------
            List[torch.Tensor], List[torch.Tensor]: assigned probabilities, only generated ids tensor
        """
        probabilities: list[torch.Tensor] = []
        output_sequences_list: list[torch.Tensor] = []
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

    def get_n_largest_tokens_and_probs(
        self, probs: "NDArray"
    ) -> list[tuple[float, str]]:
        """Get the self._n_largest_tokens_to_return largest probabilities from the probs array,
        and pair them with the corresponding str tokens.

        Args:
        ----
            probs (NDArray): array with probabilities of tokens assigned by the language model. Shape (vocab_size,)

        Returns:
        -------
            List[Tuple[float, str]]: list of tuples of the token's probability and the corresponding
                token
        """
        if probs.shape[0] != len(self.word_vocab):
            raise RuntimeError("Word vocab is populated with wrong data!")

        return nlargest(
            n=self._n_largest_tokens_to_return,
            iterable=zip((float(x) * 100 for x in probs), self.word_vocab, strict=True),
            key=lambda x: x[0],
        )
