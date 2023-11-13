import logging

from visuallm.component_base import ComponentBase
from visuallm.components.generators.base import Generator, LoadedSample
from visuallm.components.mixins.generation_selectors_mixin import (
    SELECTORS_TYPE,
    GenerationSelectorsMixin,
)
from visuallm.components.mixins.model_selection_mixin import (
    GENERATOR_CHOICES,
    ModelSelectionMixin,
)
from visuallm.elements import (
    CollapsibleElement,
    ElementBase,
    HeadingElement,
    MainHeadingElement,
    PlainTextElement,
    TableElement,
)
from visuallm.elements.selector_elements import ButtonElement, TextInputSubElement

# TODO: other than top to down linear organization


class CreateTextToTokenizerChatIsNoneError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Cannot use generator for chat because create_text_to_tokenizer_chat is None!"
        )


class ChatComponent(ComponentBase, ModelSelectionMixin, GenerationSelectorsMixin):
    def __init__(
        self,
        title: str,
        generator_choices: GENERATOR_CHOICES | None = None,
        generator: Generator | None = None,
        selectors: SELECTORS_TYPE | None = None,
        **kwargs,
    ):
        super().__init__(name="chat_component", title=title)
        main_heading_element = MainHeadingElement(content=title)
        ModelSelectionMixin.__init__(
            self,
            generator_choices=generator_choices,
            generator=generator,
        )
        self._check_generators(self.generator, generator_choices)
        GenerationSelectorsMixin.__init__(self, selectors=selectors)
        chat_elements = self.init_chat_elements()
        text_to_tokenizer_elements = self.init_text_to_tokenizer_elements()
        model_outputs_elements = self.init_model_outputs_elements()
        chat_history_elements = self.init_chat_history_elements()
        self.loaded_sample: LoadedSample = LoadedSample(user_message="", history=[])

        self.add_element(main_heading_element)
        collapsible_element = CollapsibleElement(title="Generation Settings")
        collapsible_element.add_subelements(self.generator_selection_elements)
        collapsible_element.add_subelements(self.generation_elements)
        self.add_element(collapsible_element)
        collapsible_element = CollapsibleElement(
            title="Chat History", is_collapsed=False
        )
        collapsible_element.add_subelements(chat_history_elements)
        self.add_element(collapsible_element)
        self.add_elements(chat_elements)
        self.add_elements(text_to_tokenizer_elements)
        self.add_elements(model_outputs_elements)

    def __post_init__(self, *args, **kwargs):
        pass

    def before_on_message_sent_callback(self):
        """Update loaded sample with the message from the user"""
        self.loaded_sample[
            "user_message"
        ] = self.chat_text_input_element.value_from_frontend

    def on_generation_changed_callback(self):
        self.on_message_sent_callback()

    def on_message_sent_callback(self):
        """Event that is fired when a send message button is pressed."""
        self.before_on_message_sent_callback()

        if self.generator.create_text_to_tokenizer_chat is None:
            raise CreateTextToTokenizerChatIsNoneError()

        # generate with the model
        text_to_tokenizer = self.generator.create_text_to_tokenizer_chat(
            self.loaded_sample
        )
        output = self.generator.generate_output(
            text_to_tokenizer, **self.selected_generation_parameters
        )

        # after the generation of the model
        # - text_to_tokenizer_element is updated to display the text that goes into the model
        # - model_output_display_element is updated to display model outputs
        # - button next to text input area is updated with text "Regenerate"
        # - accept generation button is enabled
        self.text_to_tokenizer_element.content = text_to_tokenizer
        self.model_output_display_element.content = output.decoded_outputs[0]
        self.chat_button_element.button_text = "Regenerate"
        self.button_accept_generation.disabled = False

    def before_on_accept_generation_callback(self):
        """Callback called just before all the common elements are changed.
        The accepted generation is added to history and chat history table is updated.
        """
        self.loaded_sample["history"].extend(
            [
                self.loaded_sample["user_message"],
                self.model_output_display_element.content,
            ]
        )
        self.update_chat_history_elements()

    def on_accept_generation_callback(self):
        """After the generation is accepted, several elements are set to empty:
        - display of the text that goes to tokenizer
        - textarea which serves for the user to input text
        - model output to accept

        Accept generation button is disabled and the sendbutton text is set to "Send Message".

        Before any action, `before_on_accept_generation_callback()` is called.
        """
        self.before_on_accept_generation_callback()

        # after accepting:
        # make all elements displaying data going directly into the model empty
        # disable accept generation button
        # change text area button to "Send Message"
        self.text_to_tokenizer_element.content = ""
        self.chat_text_input_element.value_on_backend = ""
        self.model_output_display_element.content = ""
        self.button_accept_generation.disabled = True
        self.chat_button_element.button_text = "Send Message"

    def init_chat_elements(self) -> list[ElementBase]:
        """Init elements which enable user to make text input and send it to the model."""
        self.chat_heading_element = HeadingElement("Send Message to Bot")
        self.chat_text_input_element = TextInputSubElement(
            placeholder_text="Type a message to the bot.",
            blank_after_text_send=False,
        )
        self.chat_button_element = ButtonElement(
            processing_callback=self.on_message_sent_callback,
            button_text="Send Message",
            subelements=[self.chat_text_input_element],
        )
        return [self.chat_heading_element, self.chat_button_element]

    def init_chat_history_elements(self) -> list[ElementBase]:
        chat_history_heading = HeadingElement(content="Chat History")
        self.chat_history_table = TableElement()
        return [chat_history_heading, self.chat_history_table]

    def init_model_outputs_elements(self) -> list[ElementBase]:
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

    def init_text_to_tokenizer_elements(self) -> list[ElementBase]:
        """Init elements which will display the text that is tokenized"""
        text_to_tokenizer_heading = HeadingElement("Text to Tokenizer")
        self.text_to_tokenizer_element = PlainTextElement()
        return [text_to_tokenizer_heading, self.text_to_tokenizer_element]

    def update_chat_history_elements(self):
        self.chat_history_table.clear()
        who = ["You", "Bot"]
        if len(self.loaded_sample["history"]) == 0:
            return
        self.chat_history_table.add_table(
            title="CHAT HISTORY",
            headers=["Who", "Utterance"],
            rows=[[who[i % 2], u] for i, u in enumerate(self.loaded_sample["history"])],
        )

    def _check_generators(
        self,
        generator: Generator | None,
        generator_choices: GENERATOR_CHOICES | None,
    ):
        if generator_choices is None:
            if generator is None:
                raise ValueError(
                    "Either generator_choices or generator should not be None"
                )
            generator_choices = {"default": generator}

        for _name, _generator in generator_choices.items():
            if callable(_generator):
                logging.info(f"Not checking generator '{_name}' because it is callable")
                continue

            if _generator.create_text_to_tokenizer_chat is None:
                raise CreateTextToTokenizerChatIsNoneError()
