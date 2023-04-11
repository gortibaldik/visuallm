from llm_generation_server.dialogue_connections_component import DialogueConnectionsComponent
from llm_generation_server.formatters.table_formatter import TableFormatter
from llm_generation_server.formatters.sample_selector_formatter import SampleSelectorFormatter
from flask import jsonify

class ExampleDialogueConnectionsComponent(DialogueConnectionsComponent):
    def __init__(self):
        super().__init__()
        self.sample_selector_formatter = SampleSelectorFormatter(
            0, 10
        )
        self.load_dataset_sample(0)

    def load_dataset_sample(self, sample_n: int):
        persona_headers = ["Characteristic Trait"]
        persona_rows = [
            [f"{sample_n}: I work at a bookstore. 0"],
            [f"{sample_n}: I have three tattoos. 1"],
            [f"{sample_n}: I do not drive. 2"]
        ]
        utterance_headers = ["Who", "Utterance"]
        utterance_rows = [
            ["Partner", f"{sample_n}: hi ! how are you ?"],
            ["You", f"{sample_n}: hi good and you ?"],
            ["Partner", f"{sample_n}: great ! just ran k outside ! beautiful weather !"],
            ["You", f"{sample_n}: what do you do for a living ?"],
            ["Partner", f"{sample_n}: i am in sales. you?"],
            ["You", f"{sample_n}: i work at barnes and noble"],
            ["Partner", f"{sample_n}: nice ! do you love books ?"],
            ["You", f"{sample_n}: i read all the time . bu ?"],
            ["Partner", f"{sample_n}: i have to admit , i always opted for hte movie versions of books ."],
            ["You", f"{sample_n}: do not like reading ?"],
            ["Partner", f"{sample_n}: i do , but prefer the movies . have you heard of 16 candles ?"],
            ["You", f"{sample_n}: that is old school"],
            ["Partner", f"{sample_n}: yes ... do you know if there is a book 16 candles ?"],
            ["You", f"{sample_n}: i did not know that but i have seen the movie"],
        ]
        self.table_formatter = TableFormatter()
        self.table_formatter.add_table("Persona", persona_headers, persona_rows)
        self.table_formatter.add_table("Dialogue", utterance_headers, utterance_rows)


        for j in range(10):
            for i in range(3):
                self.table_formatter.add_connection("Dialogue", j, "Persona", i, (i + 1) + 0.4, "p")
            
            for i in range(0, 14):
                if i == j:
                    continue
                self.table_formatter.add_connection("Dialogue", j, "Dialogue", i, min(i + 1, 5), "d")

