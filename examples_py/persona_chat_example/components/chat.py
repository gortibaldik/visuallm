from collections.abc import Callable

from visuallm.components.chat_component import ChatComponent as ChatComponentBase
from visuallm.elements import CollapsibleElement, ElementBase
from visuallm.elements.selector_elements import ButtonElement, ChoicesSubElement


class ChatComponent(ChatComponentBase):
    def __post_init__(
        self, *args, get_persona_traits: Callable[[], list[str]], **kwargs
    ):
        select_traits_elements = self.init_select_persona_traits_elements(
            get_persona_traits
        )
        self.add_elements(select_traits_elements, order=2.5)
        self.on_change_selected_traits()

    def update_chat_history_elements(self):
        super().update_chat_history_elements()
        self.chat_history_table.add_table(
            "BOT PERSONA",
            headers=["Trait"],
            rows=[[t] for t in self.loaded_sample["personality"]],  # type: ignore
            prepend=True,
        )

    def on_change_selected_traits(self):
        """Fired when a select persona traits button is pressed."""
        if not self.button_select_persona_traits.changed:
            return
        self.loaded_sample = {
            "personality": [  # type: ignore
                element.value_on_backend
                for element in self.button_select_persona_traits.subelements_iter
            ],
            "history": [],
        }
        self.text_to_tokenizer_element.content = ""
        self.chat_text_input_element.value_on_backend = ""
        self.model_output_display_element.content = ""
        self.update_chat_history_elements()

    def init_select_persona_traits_elements(
        self, get_persona_traits: Callable[[], list[str]]
    ) -> list[ElementBase]:
        """Init selectors of persona traits that the bot should have."""
        traits = get_persona_traits()
        collapsible_element = CollapsibleElement(title="Select Bot's Persona Traits")
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
        collapsible_element.add_subelement(self.button_select_persona_traits)
        return [collapsible_element]


def get_persona_traits() -> list[str]:
    from datasets import DatasetDict, load_dataset
    from datasets.arrow_dataset import Dataset

    dataset_dict = load_dataset("bavard/personachat_truecased")
    if not isinstance(dataset_dict, DatasetDict):
        raise TypeError()
    dataset = dataset_dict["train"]
    if not isinstance(dataset, Dataset):
        raise TypeError()
    persona_traits: set[str] = set()
    persona_traits_list: list[str] = []
    for sample in dataset:
        traits = sample["personality"]  # type: ignore
        for trait in traits:
            if trait not in persona_traits:
                persona_traits.add(trait)
                persona_traits_list.append(trait)
                if len(persona_traits) > 250:
                    return persona_traits_list
    return persona_traits_list
