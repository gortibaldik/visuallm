# Language Model Generation
- when evaluating language models it is often pain to see what is generated and why
- this little package is a `vue.js` frontend together with `flask` backend and it is designed to easily show the distribution of the next token prediction

## Installation
- right now only installation right from the git is supported, however I plan to deploy the package also to PyPi
- `pip install git+https://github.com/gortibaldik/visualize_llm_generation#egg=llm_generation_server`

## Usage
- the intended usage of this library is to inherit from `llm_generation_server.server_baseclass.FlaskGenerationApp` and to override the following methods:
    - `initialize_dictionary`: should be initialized to the dictionary used by the tokenizer for the model
    - `get_next_token_predictions`: should tokenize the current context and return the softmax output of the model
    - `append_to_context`: should handle how tokens connect to reform original sentences

### Example

```python
from llm_generation_server.server_baseclass import FlaskGenerationApp

class InteractiveGenerationServer(FlaskGenerationApp):
    def __init__(
            self,
            name,
            tokenizer: PreTrainedTokenizer,
            model: PreTrainedModel,
            initial_context: str,
            n_largest_tokens_to_return: int = 10,
        ):
        ## store tokenizer, model and initial context
        self._tokenizer = tokenizer
        self._model = model
        super().__init__(name, n_largest_tokens_to_return)
        self._context = initial_context

    def initialize_dictionary(self):
        # initialize vocabulary from tokenizer
        vocab_size = self._tokenizer.vocab_size
        self.word_dict = [""] * vocab_size
        for str_val, int_val in self._tokenizer.get_vocab().items():
            self.word_dict[int_val] = str_val

    def get_next_token_predictions(self):
        # predict with model and tokenizer
        pred_context = self._tokenizer(self._context, return_tensors="pt")
        with pt.no_grad():
            preds: pt.Tensor = self._model(**pred_context)["logits"]
            preds = pt.softmax(preds, dim=-1)

        np_preds: NDArray = preds[0, -1, :].numpy()

        # return the predictions which are mapped to the vocabulary
        return self.create_continuations(np_preds)
    
    def append_to_context(self, post_token: str):
        # append the user selection to the currently held context
        a = self._tokenizer.convert_tokens_to_string([post_token])
        self._context += a

model = load_model()
tokenizer = load_tokenizer()
initial_context = load_from_dataset()

generation_server = InteractiveGenerationServer(
    __name__,
    tokenizer,
    model,
    initial_context
)
generation_server.run()
```
![generation_image](./readme_images/generation.png)

