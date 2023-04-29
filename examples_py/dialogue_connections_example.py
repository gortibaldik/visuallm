from llm_generation_server.component_base import ComponentBase
from llm_generation_server.elements.plain_text_element import PlainTextElement
from llm_generation_server.elements.selector_elements import (
    ButtonElement,
    ChoicesSubElement,
    MinMaxSubElement,
)
from llm_generation_server.elements.table_element import TableElement


class ExampleDialogueConnectionsComponent(ComponentBase):
    def __init__(self):
        self.main_heading_element = PlainTextElement(
            is_heading=True,
            heading_level=2,
            content="Dialogue Links",
        )
        self.sample_selector_element = MinMaxSubElement(
            sample_min=0, sample_max=40, text="Select Sample:"
        )
        self.model_selector_element = ChoicesSubElement(
            choices=["first", "second", "third"], text="Select Model:"
        )
        self.selector_element = ButtonElement(
            button_text="Load Dataset Sample",
            subelements=[self.sample_selector_element, self.model_selector_element],
            endpoint_callback=self.select_sample,
        )
        self.table_element = TableElement()
        super().__init__(
            name="dialogue_links",
            title="Dialogue Links",
            elements=[
                self.main_heading_element,
                self.selector_element,
                self.table_element,
            ],
        )
        self.load_dataset_sample()

    def select_sample(self):
        self.selector_element.default_select_callback()
        self.load_dataset_sample()
        return self.fetch_info(fetch_all=False)

    def load_dataset_sample(self):
        sample_n = self.sample_selector_element.selected
        model = self.model_selector_element.selected
        persona_headers = ["Characteristic Trait"]
        persona_rows = [
            [f"[{model}] {sample_n}: I work at a bookstore."],
            [f"[{model}] {sample_n}: I have three tattoos."],
            [f"[{model}] {sample_n}: I do not drive."],
        ]
        utterance_headers = ["Who", "Utterance"]
        utterance_rows = [
            ["Partner", f"[{model}] {sample_n}: hi ! how are you ?"],
            ["You", f"[{model}] {sample_n}: hi good and you ?"],
            [
                "Partner",
                f"[{model}] {sample_n}: great ! just ran k outside ! beautiful weather !",
            ],
            ["You", f"[{model}] {sample_n}: what do you do for a living ?"],
            ["Partner", f"[{model}] {sample_n}: i am in sales. you?"],
            ["You", f"[{model}] {sample_n}: i work at barnes and noble"],
            ["Partner", f"[{model}] {sample_n}: nice ! do you love books ?"],
            ["You", f"[{model}] {sample_n}: i read all the time . bu ?"],
            [
                "Partner",
                f"[{model}] {sample_n}: i have to admit , i always opted for hte movie versions of books .",
            ],
            ["You", f"[{model}] {sample_n}: do not like reading ?"],
            [
                "Partner",
                f"[{model}] {sample_n}: i do , but prefer the movies . have you heard of 16 candles ?",
            ],
            ["You", f"[{model}] {sample_n}: that is old school"],
            [
                "Partner",
                f"[{model}] {sample_n}: yes ... do you know if there is a book 16 candles ?",
            ],
            [
                "You",
                f"[{model}] {sample_n}: i did not know that but i have seen the movie",
            ],
        ]
        self.table_element.clear()
        PERSONA_TABLE_NAME = "Persona"
        DIALOGUE_TABLE_NAME = "Dialogue Utterances"
        self.table_element.add_table(PERSONA_TABLE_NAME, persona_headers, persona_rows)
        self.table_element.add_table(
            DIALOGUE_TABLE_NAME, utterance_headers, utterance_rows
        )

        for j in range(10):
            for i in range(3):
                self.table_element.add_link_between_rows(
                    DIALOGUE_TABLE_NAME, j, PERSONA_TABLE_NAME, i, i + 1, "p"
                )

            for i in range(0, 14):
                if i == j:
                    continue
                self.table_element.add_link_between_rows(
                    DIALOGUE_TABLE_NAME, j, DIALOGUE_TABLE_NAME, i, min(i + 1, 5), "d"
                )
