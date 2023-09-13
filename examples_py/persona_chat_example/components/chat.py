from typing import List

from datasets import DatasetDict, load_dataset
from datasets.arrow_dataset import Dataset

from visuallm.components.ChatComponent import ChatComponent as ChatComponentBase
from visuallm.elements import HeadingElement
from visuallm.elements.selector_elements import ButtonElement, ChoicesSubElement

from .input_display import PersonaChatVisualization

# TODO: it would be great to add sections (which are expandable, e.g. only
# title is shown when collapsed, everything is shown when expanded)

# TODO: other than top to down linear organization


class ChatComponent(ChatComponentBase, PersonaChatVisualization):
    def __post_init__(self):
        select_traits_elements = self.init_select_persona_traits_elements()
        dialogue_vis_elements = self.init_dialogue_vis_elements()
        self.add_elements(select_traits_elements + dialogue_vis_elements, order=1.5)
        self.on_change_selected_traits()

    def on_change_selected_traits(self):
        """
        This event is fired when a select persona traits button is pressed.
        """
        if not self.button_select_persona_traits.changed:
            return
        self.loaded_sample = dict(
            personality=[
                element.selected
                for element in self.button_select_persona_traits.subelements_iter
            ],
            history=[],
        )
        self.text_to_tokenizer_element.content = ""
        self.chat_text_input_element.text_input = ""
        self.model_output_display_element.content = ""
        self.update_dialogue_structure_display(add_target=False)

    def before_on_accept_generation_callback(self):
        """This callback is called just before all the common elements are changed"""
        super().before_on_accept_generation_callback()
        self.update_dialogue_structure_display(add_target=False)

    def init_select_persona_traits_elements(self):
        """Init selectors of persona traits that the bot should have."""
        traits = get_persona_traits()
        selection_heading_element = HeadingElement(
            content="Select Bot's Persona Traits"
        )
        self.button_select_persona_traits = ButtonElement(
            self.on_change_selected_traits,
            subelements=[
                ChoicesSubElement(
                    traits[(50 * (i - 1)) : (50 * i)], f"Select Persona Trait {i}:"
                )
                for i in range(1, 6)
            ],
            button_text="Update Bot's Characteristics",
        )
        return [selection_heading_element, self.button_select_persona_traits]


def get_persona_traits() -> List[str]:
    dataset_dict = load_dataset("bavard/personachat_truecased")
    if not isinstance(dataset_dict, DatasetDict):
        raise ValueError()
    dataset = dataset_dict["train"]
    if not isinstance(dataset, Dataset):
        raise ValueError()
    persona_traits = set()
    persona_traits_list = []
    for sample in dataset:
        traits = sample["personality"]  # type: ignore
        for trait in traits:
            if trait not in persona_traits:
                persona_traits.add(trait)
                persona_traits_list.append(trait)
                if len(persona_traits) > 250:
                    return persona_traits_list
    return persona_traits_list
