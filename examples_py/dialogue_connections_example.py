from flask import jsonify, request

from llm_generation_server.component_base import ComponentBase
from llm_generation_server.formatters.plain_formatter import PlainFormatter
from llm_generation_server.formatters.sample_selector_formatter import (
    ChoicesSelectorFormatter,
    MinMaxSelectorFormatter,
)
from llm_generation_server.formatters.table_formatter import TableFormatter


class ExampleDialogueConnectionsComponent(ComponentBase):
    def __init__(self):
        self.main_heading_formatter = PlainFormatter(
            name="main_heading",
            is_heading=True,
            heading_level=2,
            content="Dialogue Links",
        )
        self.sample_selector_formatter = MinMaxSelectorFormatter(
            name="sample_selector",
            sample_min=0,
            sample_max=10,
            endpoint_url="/select_sample_dialogues",
            endpoint_callback=self.select_sample,
        )
        self.choices_selector_formatter = ChoicesSelectorFormatter(
            choices=["first", "second", "third"],
            endpoint_url="/select_model",
            endpoint_callback=self.select_model,
            name="choices_selector",
        )
        self.table_formatter = TableFormatter(name="displayed_table")
        super().__init__(
            default_url="/fetch_dialogue_links",
            name="dialogue_links",
            title="Dialogue Links",
            formatters=[
                self.main_heading_formatter,
                self.sample_selector_formatter,
                self.choices_selector_formatter,
                self.table_formatter,
            ],
        )
        self.load_dataset_sample()

    def select_sample(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        sample_n: int = request.get_json().get("sample_n")
        self.sample_selector_formatter.selected = sample_n
        self.load_dataset_sample()
        return self.fetch_info(fetch_all=False)

    def select_model(self):
        if not request.is_json:
            return jsonify(dict(result="failure"))
        model_name: str = request.get_json().get("choice")
        self.choices_selector_formatter.selected = model_name
        self.load_dataset_sample()
        return self.fetch_info(fetch_all=False)

    def load_dataset_sample(self):
        sample_n = self.sample_selector_formatter.selected
        model = self.choices_selector_formatter.selected
        persona_headers = ["Characteristic Trait"]
        persona_rows = [
            [f"[{model}] {sample_n}: I work at a bookstore. 0"],
            [f"[{model}] {sample_n}: I have three tattoos. 1"],
            [f"[{model}] {sample_n}: I do not drive. 2"],
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
        self.table_formatter.clear()
        self.table_formatter.add_table("Persona", persona_headers, persona_rows)
        self.table_formatter.add_table("Dialogue", utterance_headers, utterance_rows)

        for j in range(10):
            for i in range(3):
                self.table_formatter.add_connection(
                    "Dialogue", j, "Persona", i, (i + 1) + 0.4, "p"
                )

            for i in range(0, 14):
                if i == j:
                    continue
                self.table_formatter.add_connection(
                    "Dialogue", j, "Dialogue", i, min(i + 1, 5), "d"
                )
