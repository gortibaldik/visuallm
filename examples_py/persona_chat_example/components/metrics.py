from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import List

import torch


class Perplexity:
    def __call__(self, preds: torch.Tensor, labels: torch.Tensor):
        preds = preds.reshape((-1, preds.size(-1)))
        labels = labels.reshape((-1,))

        probs = preds[:, labels].diagonal()

        return torch.sum(-probs * torch.log(probs))


class F1Score:
    def __call__(self, preds: str, labels: str):
        return normalized_f1_measurement(preds, [labels]).F1Score


@dataclass
class F1Measurement:
    """This is a cumulative F1 measurement, hence the values can be greater
    than 1, and have to be divided by `self.Total` in order to compute macro F1
    score.

    Hence the score can be thought of as a F1 score only if `self.Total
    == 1`
    """

    Precision: float = 0
    Recall: float = 0
    F1Score: float = 0
    Total: int = 0

    def __add__(self, other: F1Measurement):
        return F1Measurement(
            self.Precision + other.Precision,
            self.Recall + other.Recall,
            self.F1Score + other.F1Score,
            self.Total + other.Total,
        )

    def take_average(self):
        """Compute macro average of all F1 scores added to this one."""
        return F1Measurement(
            self.Precision / self.Total,
            self.Recall / self.Total,
            self.F1Score / self.Total,
            1,
        )


def normalized_f1_measurement(expected: str, generated: List[str]):
    """Measure F1 on standardized word-level tokenization of generated and
    expected strings.

    Returns:
        Tuple[float, float, float]: Precision, Recall, F1-Score
    """
    expected_tokenized = normalize_answer(expected).split()
    p, r, f = 0, 0, 0
    for g in generated:
        generated_tokenized = normalize_answer(g).split()
        pg, rg, fg = calculate_f1_on_lists(expected_tokenized, generated_tokenized)
        p, r, f = p + pg, r + rg, f + fg
    return F1Measurement(p, r, f, len(generated))


def calculate_f1_on_lists(gold: List[str], predicted: List[str]):
    """From a list of words calculate word level precision and recall, and
    finaly an F1 score."""
    common = Counter(gold) & Counter(predicted)
    num_same = sum(common.values())
    if num_same == 0:
        return 0, 0, 0

    precision = 1.0 * num_same / len(predicted)
    recall = 1.0 * num_same / len(gold)

    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1


# adapted from:
# https://github.com/SivilTaram/Persona-Dialogue-Generation/blob/master/parlai/core/metrics.py
re_art = re.compile(r"\b(a|an|the)\b")
re_punc = re.compile(r'[!"#$%&()*+,-./:;<=>?@\[\]\\^`{|}~_\']')


def remove_articles(text):
    return re_art.sub(" ", text)


def white_space_fix(text):
    return " ".join(text.split())


def remove_punc(text):
    return re_punc.sub(" ", text)  # convert punctuation to spaces


def lower(text):
    return text.lower()


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    return white_space_fix(remove_articles(remove_punc(lower(s))))
