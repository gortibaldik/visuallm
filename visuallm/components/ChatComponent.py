from typing import Any, Dict, List, Optional

from visuallm.component_base import ComponentBase
from visuallm.components.mixins.generation_selectors_mixin import (
    SELECTORS_TYPE,
    GenerationSelectorsMixin,
)
from visuallm.components.mixins.Generator import Generator
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements import (
    ElementBase,
    HeadingElement,
    MainHeadingElement,
    PlainTextElement,
    TextInputElement,
)
from visuallm.elements.selector_elements import ButtonElement

# from visuallm.components.ChatComponent import ChatComponent as ChatComponentBase

# TODO: it would be great to add sections (which are expandable, e.g. only
# title is shown when collapsed, everything is shown when expanded)

# TODO: other than top to down linear organization


class ChatComponent(ComponentBase, ModelSelectionMixin, GenerationSelectorsMixin):
    def __init__(
        self,
        title: str,
        generator_choices: Optional[GENERATOR_CHOICES] = None,
        generator: Optional[Generator] = None,
        selectors: SELECTORS_TYPE = {},
    ):
        super().__init__(name="chat_component", title=title)
        main_heading_element = MainHeadingElement(content=title)
        ModelSelectionMixin.__init__(
            self,
            generator_choices=generator_choices,
            generator=generator,
        )
        GenerationSelectorsMixin.__init__(self, selectors=selectors)
        chat_elements = self.init_chat_elements()
        text_to_tokenizer_elements = self.init_text_to_tokenizer_elements()
        model_outputs_elements = self.init_model_outputs_elements()
        self.loaded_sample: Dict[str, Any] = dict(history=[], user_message="")

        self.add_element(main_heading_element)
        self.add_elements(self.generation_elements)
        self.add_elements(chat_elements)
        self.add_elements(text_to_tokenizer_elements)
        self.add_elements(model_outputs_elements)

    def __post_init__(self):
        pass

    def before_on_message_sent_callback(self):
        """Update loaded sample with the message from the user"""
        self.loaded_sample["user_message"] = self.chat_text_input_element.text_input

    def on_generation_changed_callback(self):
        self.on_message_sent_callback()

    def on_message_sent_callback(self):
        """
        This event is fired when a send message button is pressed.
        """
        self.before_on_message_sent_callback()

        # generate with the model
        text_to_tokenizer = self.generator.create_text_to_tokenizer(self.loaded_sample)
        output = self.generator.generate_output(
            text_to_tokenizer, **self.selected_generation_parameters
        )

        # after the generation of the model
        # - text_to_tokenizer_element is updated to display the text that goes into the model
        # - model_output_display_element is updated to display model outputs
        # - button next to text input area is updated with text "Regenerate"
        # - accept generation button is enabled
        self.text_to_tokenizer_element.content = text_to_tokenizer
        self.model_output_display_element.content = output["decoded_outputs"][0]
        self.chat_text_input_element.button_text = "Regenerate"
        self.button_accept_generation.disabled = False

    def before_on_accept_generation_callback(self):
        """This callback is called just before all the common elements are changed"""
        self.loaded_sample["history"].extend(
            [
                self.loaded_sample["user_message"],
                self.model_output_display_element.content,
            ]
        )

    def on_accept_generation_callback(self):
        """After the generation is accepted, the messages in TODO: complete docstring"""

        self.before_on_accept_generation_callback()

        # after accepting:
        # make all elements displaying data going directly into the model empty
        # disable accept generation button
        # change text area button to "Send Message"
        self.text_to_tokenizer_element.content = ""
        self.chat_text_input_element.text_input = ""
        self.model_output_display_element.content = ""
        self.button_accept_generation.disabled = True
        self.chat_text_input_element.button_text = "Send Message"

    def init_chat_elements(self) -> List[ElementBase]:
        """Init elements which enable user to make text input and send it to the model."""
        self.chat_text_input_element = TextInputElement(
            processing_callback=self.on_message_sent_callback,
            button_text="Send Message",
            default_text="Type a message to the bot.",
        )
        return [self.chat_text_input_element]

    def init_model_outputs_elements(self) -> List[ElementBase]:
        """Init elements which show the outputs of the model."""
        model_output_display_heading = HeadingElement(content="Model Output")
        self.model_output_display_element = PlainTextElement()
        self.button_accept_generation = ButtonElement(
            self.on_accept_generation_callback,
            button_text="Accept Generation",
            disabled=True,
        )
        return [
            model_output_display_heading,
            self.model_output_display_element,
            self.button_accept_generation,
        ]

    def init_text_to_tokenizer_elements(self) -> List[ElementBase]:
        """Init elements which will display the text that is tokenized"""
        text_to_tokenizer_heading = HeadingElement("Text to Tokenizer")
        self.text_to_tokenizer_element = PlainTextElement()
        return [text_to_tokenizer_heading, self.text_to_tokenizer_element]
