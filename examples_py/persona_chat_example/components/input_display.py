import copy
from typing import Any

from visuallm.elements.element_base import ElementBase
from visuallm.elements.plain_text_element import HeadingElement
from visuallm.elements.table_element import TableElement


class PersonaChatVisualization:
    def __init__(self) -> None:
        # just for the typechecker to not complain
        self.loaded_sample: Any = 1

    def init_dialogue_vis_elements(self) -> list[ElementBase]:
        """Init elements which display the personachat tables."""
        table_input_heading = HeadingElement(content="Structure of Dialogue")
        self.input_table_vis = TableElement()
        return [table_input_heading, self.input_table_vis]

    def update_dialogue_structure_display(self, add_target: bool = True):
        """Update elements which display the personachat tables."""
        sample = self.loaded_sample
        context = copy.deepcopy(sample["history"])
        if add_target:
            context.append(sample["candidates"][-1])
        persona = sample["personality"]

        self.set_sample_tables_element(persona, context)

    def set_sample_tables_element(
        self, persona: list[str], context: list[str], other_last: bool = False
    ):
        """Populate the tables with the information from the dataset sample."""
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
                "Turns",
                ["Who", "Turn"],
                [[w, u] for w, u in zip(whos, context, strict=True)],
            )
