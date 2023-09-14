# Conditional Language Model Generation Visualization

- when evaluating language models it is often pain to see what is generated and why
- this little package is a `vue.js` frontend together with `flask` backend and it is designed to easily show some interesting visualizations on conditional generation models
- it handles frontend-backend communication as well as frontend rendering
- hence the developper can focus only on ML aspects of his work!

![example workflow](https://github.com/gortibaldik/visuallm/actions/workflows/python-test.yaml/badge.svg)

## VERSION: `0.3.0` changelog

- added `visuallm.components.ChatComponent`, so you can now chat with the models!
- added support for OpenAI API, so providing the token, you can chat with the OpenAI models!
- refactoring and better code quality
- more documentation strings

## Installation

- install from pypi:
  - `pip install visuallm`

## Usage

_The documentation is a WIP as of now, however here you can see several snippets of what the library can do._

### Alpaca Example

The first workflow that we'll show is the workflow where you don't alter the implementation of the components at all and just use the provided components.

#### Run Instructions

The alpaca example code can be found here: [`./examples_py/alpaca_example`](./examples_py/alpaca_example/), the code can be started by running `flask --app examples_py.alpaca_example.app run`.

We'll use `alpaca` dataset and `gpt2` model as those are reasonably small to run even on less performant computers.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./examples_py/alpaca_example/app.py&lines=14-19&header=# ./examples_py/alpaca_example/app.py lines 14-19)-->
<!-- MARKDOWN-AUTO-DOCS:END-->

All the datasets are different, therefore we expect the user to provide 3 functions, which
define how the text which is tokenized is constructed, how the text for the one step prediction
is constructed, and how the target text is constructed.

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./examples_py/alpaca_example/app.py&lines=22-41&header=# ./examples_py/alpaca_example/app.py lines 22-41)-->
<!-- MARKDOWN-AUTO-DOCS:END-->

Instantiate all the components from the library and run the server

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./examples_py/alpaca_example/app.py&lines=44-57&header=# ./examples_py/alpaca_example/app.py lines 44-57)-->
<!-- MARKDOWN-AUTO-DOCS:END-->

#### Dataset Visualization (Screenshots)

![dataset_visualization](./readme_images/alpaca_dataset_vis.png)

#### Generation (Screenshots)

![generation](./readme_images/alpaca_generation.png)

#### Next Token Prediction (Screenshots)

![next_token_prediction](./readme_images/alpaca_next_token.png)

### PersonaChat Example

The second workflow that we'll show is the workflow where you alter the implementation of the components, so that the dataset sample is shown in a different way.

If you want to use the app with the personachat dataset, you can play with prepared example by running: `flask --app examples_py.persona_chat_example.app run`.

#### Generation Playground

Select which parameters you want to use for generation, plug in a `HuggingFace` model, or an `OpenAI` token and have fun with experimenting with various generation hyperparameters!

![gen_params](./readme_images/gen_params.png)
![generation](./readme_images/generations_openai.png)

#### Chat Playground

Select which parameters you want to use for generation, plug in a `HuggingFace` model, or an `OpenAI` token and have fun with chatting with the model!

![chat](./readme_images/chat.png)

#### Visualize Next Token Predictions

By using `visuallm.components.NextTokenPredictionComponent.NextTokenPredictionComponent` you can just plug the HuggingFace model in and go through the generation process step by step.

![next_token_prediction](./readme_images/next_token_probs.png)
