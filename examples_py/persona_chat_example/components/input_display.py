from typing import Any, List

from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.table_element import TableElement


class PersonaChatVisualization:
    def __init__(self):
        # just for the typechecker to not complain
        self.loaded_sample: Any = 1

    def init_model_input_display(self) -> List[ElementBase]:
        self.input_table_vis = TableElement()
        self.input_heading = PlainTextElement(is_heading=True, content="Model Inputs")
        self.input_content = PlainTextElement()
        return [
            self.input_table_vis,
            self.input_heading,
            self.input_content,
        ]

    def update_model_input_display(self, add_target: bool = True):
        sample = self.loaded_sample
        context = sample["history"]
        if add_target:
            context.append(sample["candidates"][-1])
        persona = sample["personality"]

        sentences = [s for part in [persona, context] for s in part]

        self.input_content.content = " ".join(sentences)
        self.set_sample_tables_element(persona, context)

    def set_sample_tables_element(
        self, persona: List[str], context: List[str], other_last: bool = False
    ):
        self.input_table_vis.clear()

        self.input_table_vis.add_table(
            title="BOT Persona",
            headers=["Trait"],
            rows=[[t] for t in persona],
        )

        d_len = len(context)  # dialogue length
        bot_on_odd = int(d_len % 2 == (1 if not other_last else 0))
        whos = ["BOT" if i % 2 == bot_on_odd else "OTHER" for i in range(d_len)]

        if len(context) > 0:
            self.input_table_vis.add_table(
                "Turns", ["Who", "Turn"], [[w, u] for w, u in zip(whos, context)]
            )
