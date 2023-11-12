import copy

from visuallm.components.ChatComponent import ChatComponent, LoadedSample
from visuallm.components.generators.openai import OpenAIGenerator, OpenAIMessage
from visuallm.components.mixins.generation_selectors_mixin import (
    SELECTORS_TYPE,
    MinMaxSelectorType,
)
from visuallm.server import Server


def create_text_to_tokenizer_openai(loaded_sample: LoadedSample) -> str:
    api_message = OpenAIMessage(model="gpt-3.5-turbo-0613")
    api_message.messages = copy.deepcopy(loaded_sample["history"])
    api_message.messages.append(loaded_sample["user_message"])

    return api_message.construct_message()


generator = OpenAIGenerator(
    create_text_to_tokenizer_chat=create_text_to_tokenizer_openai
)
selectors: SELECTORS_TYPE = {
    "top_p": MinMaxSelectorType(0, 1, default_value=1.0, step_size=0.05),
    "max_new_tokens": MinMaxSelectorType(10, 100, default_value=30),
    "temperature": MinMaxSelectorType(0, 2, default_value=1.0, step_size=0.1),
}
chat_component = ChatComponent(
    title="Chat",
    generator=generator,
    selectors=selectors,
)
server = Server(__name__, components=[chat_component])
app = server.app
