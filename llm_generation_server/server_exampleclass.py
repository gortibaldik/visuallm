from llm_generation_server.server_baseclass import FlaskGenerationApp
import requests
import random
import numpy as np

class FlaskGenerationExampleApp(FlaskGenerationApp):
    def initialize_vocab(self):
        word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
        response = requests.get(word_site)
        self.word_dict = response.content.splitlines()
        self.word_dict = [x.decode('utf-8') for x in self.word_dict]
        self.ix_arr = list(range(len(self.word_dict)))
    
    def append_to_context(self, context: str, post_token: str):
        context = context + " " + post_token
        return context
    
    def format_context(self, context: str):
        return "<br>".join(context.split())

    def get_next_token_predictions(self, context: str):
        K = self.n_largest_tokens_to_return * 3
        twenty_ixes = random.choices(self.ix_arr, k=K)
        twenty_probs = [random.random() for _ in range(K)]
        twenty_probs = np.exp(twenty_probs)
        twenty_probs /= np.sum(twenty_probs)
        probs = np.zeros((len(self.word_dict, )))
        probs[twenty_ixes] = twenty_probs
        return self.create_continuations(probs)