from typing import Any, List

from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.table_element import TableElement


class PersonaChatVisualization:
    def __init__(self):
        self._loaded_sample: Any = 1

    def init_model_input_display(self) -> List[ElementBase]:
        self.table_element = TableElement()
        self.initial_context_raw_heading = PlainTextElement(
            is_heading=True, content="Model Inputs"
        )
        self.intial_context_raw_element = PlainTextElement()
        return [
            self.table_element,
            self.initial_context_raw_heading,
            self.intial_context_raw_element,
        ]

    def update_model_input_display(self, add_target: bool = True):
        sample = self._loaded_sample
        context = sample["history"]
        if add_target:
            context.append(sample["candidates"][-1])
        persona = sample["personality"]

        sentences = [s for part in [persona, context] for s in part]

        self.intial_context_raw_element.content = " ".join(sentences)
        self.set_sample_tables_element(persona, context)

    def set_sample_tables_element(
        self, persona: List[str], context: List[str], other_last: bool = False
    ):
        self.table_element.clear()

        self.table_element.add_table(
            title="BOT Persona",
            headers=["Trait"],
            rows=[[t] for t in persona],
        )

        d_len = len(context)  # dialogue length
        bot_on_odd = int(d_len % 2 == (1 if not other_last else 0))
        whos = ["BOT" if i % 2 == bot_on_odd else "OTHER" for i in range(d_len)]

        if len(context) > 0:
            self.table_element.add_table(
                "Turns", ["Who", "Turn"], [[w, u] for w, u in zip(whos, context)]
            )
