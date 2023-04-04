from llm_generation_server.server import Server
from flask import jsonify, request
from typing import List
from heapq import nlargest
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Continuation:
    token: str
    prob: float

class NextTokenPredictionComponent(ABC):
    def __init__(self, n_largest_tokens_to_return: int = 10):
        self.n_largest_tokens_to_return = n_largest_tokens_to_return

    def init_app(self, app: Server):
        self.app = app
        self.app.add_endpoint(
            "/fetch",
            self.fetch,
            methods=['GET']
        )
        self.app.add_endpoint(
            "/select",
            self.select,
            methods=['POST']
        )
    
    def fetch(self):
        return jsonify(dict(
            result="success",
            context=self.format_context(self._context),
            continuations=self.get_next_token_predictions(self._context)
        ))
    
    def select(self):
        data = request.get_json()
        post_token = data.get('token')
        self._context = self.append_to_context(self._context, post_token)

        return jsonify(dict(
            result="success",
            context = self.format_context(self._context),
            continuations=self.get_next_token_predictions(self._context)
        ))

    def initialize_context(self, context:str):
        self._context = context

    def format_context(self, context: str):
        return context
    
    def create_continuations(self, probs: List[float]):
        n_largest = nlargest(
            self.n_largest_tokens_to_return,
            zip(probs, self.word_dict),
            key=lambda x: x[0]
        )
        return [Continuation(x[1], x[0] * 100) for x in n_largest]
    
    @abstractmethod
    def initialize_vocab(self):
        ...
    
    @abstractmethod
    def append_to_context(self, context: str, post_token: str):
        ...

    @abstractmethod
    def get_next_token_predictions(self, context: str):
        ...