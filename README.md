# Conditional Language Model Generation Visualization

- when evaluating language models it is often pain to see what is generated and why
- this little package is a `vue.js` frontend together with `flask` backend and it is designed to easily show some interesting visualizations on conditional generation models
- it handles frontend-backend communication as well as frontend rendering
- hence the developper can focus only on ML aspects of his work!

![example workflow](https://github.com/gortibaldik/visuallm/actions/workflows/python-test.yaml/badge.svg)

## VERSION: `0.2.1` changelog

- added `visuallm.elements.text_input_element.TextInputElement`
- refactoring and better code quality
- resolved one dependabot alert

## Installation

- install from pypi:
  - `pip install visuallm`

## Usage

_The documentation is a WIP as of now, however here you can see several snippets of what the library can do._

### Generation Playground

Select which parameters you want to use for generation, plug in a `HuggingFace` model, or an `OpenAI` token and have fun with experimenting with various generation hyperparameters!

![gen_params](./readme_images/gen_params.png)
![generation](./readme_images/generations_openai.png)

### Chat Playground

Select which parameters you want to use for generation, plug in a `HuggingFace` model, or an `OpenAI` token and have fun with chatting with the model!

![chat](./readme_images/chat.png)

### Visualize Next Token Predictions

By using `visuallm.components.NextTokenPredictionComponent.NextTokenPredictionComponent` you can just plug the HuggingFace model in and go through the generation process step by step.

![next_token_prediction](./readme_images/next_token_probs.png)
