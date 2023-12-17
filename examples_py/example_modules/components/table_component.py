from visuallm.component_base import ComponentBase
from visuallm.elements.plain_text_element import MainHeadingElement
from visuallm.elements.table_element import LinkBetweenRows, TableElement


class TableComponent(ComponentBase):
    def __init__(self):
        super().__init__(name="table_component", title="Table Component")
        self._initialize_table_element()
        self.add_element(MainHeadingElement(content="Table Component"))
        self.add_element(self.table_element)

    def _initialize_table_element(self):
        """Create a simple table with links pointing to all the rows upwards"""
        self.table_element = TableElement()

        # create a table with headers
        headers = ["No.", "Turn", "Another", "Column"]
        rows = [
            [i, x, f"Another-{i+1}.", f"Column-{i+1}."]
            for i, x in enumerate(
                [
                    "This is first row",
                    "This is second row",
                    "This is third row",
                    "This is fourth row",
                    "This is fifth row",
                    "This is row with `<html>` `<tags>`",
                    "This is a multi line\nrow so it should be\ndisplayed on multiple lines.",
                    "Another Row just because",
                    "And another one",
                ]
            )
        ]
        self.table_element.clear()
        table_name = "Table1 is a Great Table"
        self.table_element.add_table(table_name, headers, rows)

        # add links pointing to all the rows upwards
        for j in range(len(rows) - 1, 0, -1):
            for i in range(j):
                self.table_element.add_link_between_rows(
                    LinkBetweenRows(table_name, j, table_name, i, Label="some value")
                )
