from llm_generation_server.dialogue_connections_component import DialogueConnectionsComponent
from llm_generation_server.table_formatter import TableFormatter
from flask import jsonify

class ExampleDialogueConnectionsComponent(DialogueConnectionsComponent):
    def __init__(self):
        persona_headers = ["Characteristic Trait"]
        persona_rows = [
            ["I work at a bookstore. 0"],
            ["I have three tattoos. 1"],
            ["I do not drive. 2"]
        ]
        utterance_headers = ["Who", "Utterance"]
        utterance_rows = [
            ["Partner", "hi ! how are you ?"],
            ["You", "hi good and you ?"],
            ["Partner", "great ! just ran k outside ! beautiful weather !"],
            ["You", "what do you do for a living ?"],
            ["Partner", "i am in sales. you?"],
            ["You", "i work at barnes and noble"],
            ["Partner", "nice ! do you love books ?"],
            ["You", "i read all the time . bu ?"],
            ["Partner", "i have to admit , i always opted for hte movie versions of books ."],
            ["You", "do not like reading ?"],
            ["Partner", "i do , but prefer the movies . have you heard of 16 candles ?"],
            ["You", "that is old school"],
            ["Partner", "yes ... do you know if there is a book 16 candles ?"],
            ["You", "i did not know that but i have seen the movie"],
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
