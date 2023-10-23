import heapq
import math
import random

import requests

from visuallm.component_base import ComponentBase
from visuallm.elements.barchart_element import BarChartElement, PieceInfo
from visuallm.elements.plain_text_element import PlainTextElement


class BarChartComponentSimple(ComponentBase):
    def __init__(self, long_contexts: bool = False, title="BarChart Component"):
        super().__init__(name="barchart_component", title=title)
        self.word_vocab, self.word_ids = download_word_vocabulary()
        self.barchart_element = BarChartElement(
            processing_callback=self.barchart_callback, long_contexts=long_contexts
        )
        self.text_element = PlainTextElement()
        self.add_elements([self.barchart_element, self.text_element])
        self.update_barchart_component()

    def update_barchart_component(self):
        probs = sample_ten_words(self.word_ids)
        top_k = 10
        ten_largest_probs = heapq.nlargest(
            top_k, zip(*zip(*probs), self.word_vocab)  # noqa: B905
        )

        piece_infos = []
        for i in range(top_k):
            piece_infos.append(
                PieceInfo(
                    pieceTitle=ten_largest_probs[i][1],
                    barHeights=[ten_largest_probs[i][0]],
                    barAnnotations=[f"{ten_largest_probs[i][0]:.2f}%"],
                    barNames=[""],
                )
            )

        self.barchart_element.set_piece_infos(piece_infos)

    def barchart_callback(self):
        s = self.barchart_element.selected
        self.text_element.content = f"Last selected: {s}"
        self.update_barchart_component()


def download_word_vocabulary():
    """Download MIT word list as a word vocab.

    Returns
    -------
        Tuple[List[str], List[int]]: list of words and list of indices of the
            corresponding words
    """
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = requests.get(word_site, timeout=10)
    word_vocab = [x.decode("utf-8") for x in response.content.splitlines()]
    word_ids = [i for i, _ in enumerate(word_vocab)]
    return word_vocab, word_ids


def sample_ten_words(word_ids):
    """Sample 10 random ids from word_ids and give them 10 random exponentialy
    distributed probabilities.
    """
    k = 10
    ten_samples = random.choices(word_ids, k=k)  # noqa: S311
    ten_numbers = [math.exp(i + random_noise()) for i in range(k)]
    ten_numbers_sum = sum(ten_numbers)
    ten_probs = [n / ten_numbers_sum for n in ten_numbers]

    probs = [[0.0] for _ in word_ids]
    for i, p in zip(ten_samples, ten_probs, strict=True):
        probs[i][0] = p * 100
    return probs


def random_noise(lower_bound=-1, upper_bound=1):
    """Create random noise between lower_bound and upper bound."""
    if lower_bound >= upper_bound:
        raise ValueError()
    range_size = upper_bound - lower_bound
    noise = random.random() * range_size + lower_bound  # noqa: S311
    return noise
