from llm_generation_server.component_base import ComponentBase
from llm_generation_server.elements.plain_text_element import PlainTextElement
from llm_generation_server.elements.table_element import TableElement


class TableComponent(ComponentBase):
    def __init__(self):
        self._initialize_table_component()
        super().__init__(
            name="table_component",
            title="Table Component",
            elements=[
                PlainTextElement(
                    is_heading=True, heading_level=2, content="Table Component"
                ),
                self.table_element,
            ],
        )

    def _initialize_table_component(self):
        """Create a simple table with links pointing to all the rows upwards"""
        self.table_element = TableElement()

        # create a table with headers
        headers = ["No.", "Turn"]
        rows = [
            [i, x]
            for i, x in enumerate(
                [
                    "This is first row",
                    "This is second row",
                    "This is third row",
                    "This is fourth row",
                    "This is fifth row",
                ]
            )
        ]
        self.table_element.clear()
        TABLE_NAME = "Table1 is a Great Table"
        self.table_element.add_table(TABLE_NAME, headers, rows)

        # add links pointing to all the rows upwards
        for j in range(len(rows) - 1, 0, -1):
            for i in range(j):
                self.table_element.add_link_between_rows(
                    TABLE_NAME, j, TABLE_NAME, i, 3, "some value"
                )
