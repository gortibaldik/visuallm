from llm_generation_server.next_token_prediction_component import NextTokenPredictionComponent
from llm_generation_server.formatters.table_formatter import TableFormatter
import requests
import random
import numpy as np

class ExampleNextTokenPredictionComponent(NextTokenPredictionComponent):
    def __init__(self):
        super().__init__()
        self.load_dataset_sample(0)

    def initialize_vocab(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.word_vocab = response.content.splitlines()
        self.word_vocab = [x.decode('utf-8') for x in self.word_vocab]
        self.ix_arr = list(range(len(self.word_vocab)))

    def before_select_response(self, post_token: str):
        self.generated_formatter.content += " " + post_token
        probs = self.get_next_token_predictions()
        self.process_predictions(probs)

    def before_fetch_response(self):
        probs = self.get_next_token_predictions()
        self.process_predictions(probs)

    def load_dataset_sample(self, sample_n: int):
        headers = ["No.", "Turn"]
        rows = [ [i, x] for i, x in enumerate([
                f"{sample_n}: This is first row",
                f"{sample_n}: This is second row",
                f"{sample_n}: This is third row",
                f"{sample_n}: This is fourth row",
                f"{sample_n}: This is fifth row"
            ])
        ]
        self.initial_context_formatter = TableFormatter()
        self.initial_context_formatter.add_table(
            "Longer Context",
            headers, rows
        )
        self.generated_formatter.content = ""

        for j in range(len(rows) - 1, 0, -1):
            for i in range(j):
                self.initial_context_formatter.add_connection(
                    "Longer Context",
                    j,
                    "Longer Context",
                    i,
                    3,
                    "nn"
                  )

    def process_predictions(self, probs):
        words = self.softmax_formatter.assign_words_to_probs(
            probs,
            self.word_vocab
        )
        self.softmax_formatter.possibilities = words

    def get_next_token_predictions(self):
        n = self.softmax_formatter.n_largest_tokens_to_return
        K = n * 3
        twenty_ixes = random.choices(self.ix_arr, k=K)
        twenty_probs = [random.random() for _ in range(K)]
        twenty_probs = np.exp(twenty_probs)
        twenty_probs /= np.sum(twenty_probs)
        probs = np.zeros((len(self.word_vocab, )))
        probs[twenty_ixes] = twenty_probs
        return probs