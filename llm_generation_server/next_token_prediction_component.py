from llm_generation_server.server import Server
from flask import jsonify, request
from abc import ABC, abstractmethod
from llm_generation_server.formatters.plain_formatter import PlainFormatter
from llm_generation_server.formatters.softmax_formatter import SoftmaxFormatter
from llm_generation_server.formatters.sample_selector_formatter import SampleSelectorFormatter


class NextTokenPredictionComponent(ABC):
    def __init__(self, n_largest_tokens_to_return: int=10, min_sample_n=0, max_sample_n=10):
        self.initial_context_formatter = PlainFormatter()
        self.generated_formatter = PlainFormatter()
        self.softmax_formatter = SoftmaxFormatter(n_largest_tokens_to_return)
        self.sample_selector_formatter = SampleSelectorFormatter(min_sample_n, max_sample_n)

    def init_app(self, app: Server):
        self.app = app
        self.app.add_endpoint(
            "/fetch_next_token_prediction",
            self.fetch,
            methods=['GET']
        )
        self.app.add_endpoint(
            "/select_next_token_prediction",
            self.select,
            methods=['POST']
        )
        self.app.add_endpoint(
            "/select_dataset_sample_next_token_prediction",
            self.select_dataset_sample,
            methods=['POST']
        )
    
    @property
    def name(self):
        return "next_token_prediction"

    @property
    def title(self):
        return "Next Token Prediction"
    
    def fetch(self):
        self.before_fetch_response()
        return jsonify(dict(
            result="success",
            initial_context=self.initial_context_formatter.format(),
            generated_context=self.generated_formatter.format(),
            continuations=self.softmax_formatter.format(),
            sample_selector=self.sample_selector_formatter.format()
        ))
    
    def select(self):
        data = request.get_json()
        post_token: str = data.get('token')
        self.before_select_response(post_token)

        return jsonify(dict(
            result="success",
            generated_context=self.generated_formatter.format(),
            continuations=self.softmax_formatter.format()
        ))

    def select_dataset_sample(self):
        data = request.get_json()
        sample_n: int = data.get('sample_n')
        self.load_dataset_sample(sample_n)
        return self.fetch()
    
    @abstractmethod
    def load_dataset_sample(self, sample_n: int):
        ...
    
    @abstractmethod
    def initialize_vocab(self):
        """Initialize vocabulary used by `assign_words_to_probs` to
        display `self.n_largest_tokens_to_return` tokens with highest
        probability.

        This method should initialize `self.word_vocab`.
        """
        ...
    
    @abstractmethod
    def before_select_response(self, post_token: str):
        ...

    @abstractmethod
    def before_fetch_response(self):
        ...
