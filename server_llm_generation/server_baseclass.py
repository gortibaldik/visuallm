from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from typing import Callable, List
from dataclasses import dataclass
from heapq import nlargest
import requests
import random
import numpy as np

@dataclass
class Continuation:
    token: str
    prob: float


class FlaskGenerationApp:
    def retrieve_module_path(self):
        try:
            import llm_generation_server
            print(llm_generation_server.__file__)
        except:
            print("nothing imported")

    def __init__(self, name, n_largest_tokens_to_return: int=10):
        self.retrieve_module_path()
        self.app = Flask(
            name,
            static_url_path="",
            static_folder="dist/",
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
        self.initialize_dictionary()
        self.ix_arr = list(range(len(self.word_dict)))
        self._context = "This is a context from the server"

    def initialize_dictionary(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.word_dict = response.content.splitlines()
        self.word_dict = [x.decode('utf-8') for x in self.word_dict]

    def fetch(self):
        dct = dict(
            result="success",
            context=self._context,
            continuations=self.get_next_token_predictions()
        )
        print(dct)
        return jsonify(dct)
    
    def select(self):
        data = request.get_json()
        post_token = data.get('token')
        self._context += " " + post_token

        return jsonify(dict(
            result="success",
            context = self._context,
            continuations=self.get_next_token_predictions()
        ))
    
    def create_continuations(self, probs: List[float]):
        n_largest = nlargest(
            self.n_largest_tokens_to_return,
            zip(probs, self.word_dict),
            key=lambda x: x[0]
        )
        return [Continuation(x[1], x[0] * 100) for x in n_largest]

    def get_next_token_predictions(self):
        K = self.n_largest_tokens_to_return * 3
        twenty_ixes = random.choices(self.ix_arr, k=K)
        twenty_probs = [random.random() for _ in range(K)]
        twenty_probs = np.exp(twenty_probs)
        twenty_probs /= np.sum(twenty_probs)
        probs = np.zeros((len(self.word_dict, )))
        probs[twenty_ixes] = twenty_probs
        return self.create_continuations(probs)

    def run(self):
        self.app.run()
    
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