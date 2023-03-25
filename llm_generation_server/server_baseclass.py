from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from typing import Callable, List
from dataclasses import dataclass
from heapq import nlargest
import os
import sys
from abc import ABC, abstractmethod

@dataclass
class Continuation:
    token: str
    prob: float


class FlaskGenerationApp(ABC):
    def __init__(self, name, n_largest_tokens_to_return: int=10):
        self.app = Flask(
            name,
            static_url_path="",
            static_folder=self._retrieve_static_files_path(),
            )
        self.n_largest_tokens_to_return = n_largest_tokens_to_return
        self.add_endpoint(
            "/fetch",
            self.fetch,
            methods=['GET']
        )
        self.add_endpoint(
            "/select",
            self.select,
            methods=['POST']
        )
        self.add_endpoint(
            "/",
            lambda: redirect("/index.html", code=302),
            methods=['GET']
        )
        CORS(self.app, resources={r'/*': {'origins': '*'}})

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

    def run(self):
        self.app.run()

    def initialize_context(self, context:str):
        self._context = context
    
    def format_context(self, context: str):
        return context
    
    def add_endpoint(
        self,
        url_name: str,
        f: Callable,
        methods: List[str],
    ):
        self.app.add_url_rule(
            rule=url_name,
            endpoint=None,
            view_func=f,
            methods=methods
        )
    
    def create_continuations(self, probs: List[float]):
        n_largest = nlargest(
            self.n_largest_tokens_to_return,
            zip(probs, self.word_dict),
            key=lambda x: x[0]
        )
        return [Continuation(x[1], x[0] * 100) for x in n_largest]
    
    def _retrieve_static_files_path(self):
        dirname = os.path.dirname(__file__)
        static_path = os.path.join(dirname, "dist")
        print(f"Serving static files from {static_path}", file=sys.stderr)
        return static_path

    @abstractmethod
    def initialize_vocab(self):
        ...
    
    @abstractmethod
    def append_to_context(self, context: str, post_token: str):
        ...

    @abstractmethod
    def get_next_token_predictions(self, context: str):
        ...
