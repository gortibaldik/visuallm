from visuallm.component_base import ComponentBase
from visuallm.elements.plain_text_element import PlainTextElement
from visuallm.elements.table_element import Colors, LinkBetweenRows, TableElement


class TwoTablesComponent(ComponentBase):
    def __init__(self):
        self._initialize_table_element()
        super().__init__(
            name="table_component",
            title="Two Tables Component",
            elements=[
                PlainTextElement(
                    is_heading=True, heading_level=2, content="Table Component"
                ),
                self.table_element,
            ],
        )

    def _initialize_table_element(self):
        """Create a simple table with links pointing to all the rows upwards"""
        self.table_element = TableElement()

        # create n tables with headers
        NUMBER_OF_TABLES = 2
        headers = ["No.", "Turn"]
        rows = [
            [
                [i, x]
                for i, x in enumerate(
                    [
                        f"(Table {table_n}) This is first row",
                        f"(Table {table_n}) This is second row",
                        f"(Table {table_n}) This is third row",
                        f"(Table {table_n}) This is fourth row",
                        f"(Table {table_n}) This is fifth row",
                    ]
                )
            ]
            for table_n in range(NUMBER_OF_TABLES)
        ]
        TABLE_NAMES = [
            f"Table{table_n} is a Great Table" for table_n in range(NUMBER_OF_TABLES)
        ]
        self.table_element.clear()

        for i in range(NUMBER_OF_TABLES):
            self.table_element.add_table(TABLE_NAMES[i], headers, rows[i])

        # add links pointing from the rows of the first table to all the rows
        # of the first table upwards
        for j in range(len(rows[0]) - 1, 0, -1):
            for i in range(j):
                self.table_element.add_link_between_rows(
                    LinkBetweenRows(
                        TABLE_NAMES[0],
                        j,
                        TABLE_NAMES[0],
                        i,
                        Importance=1,
                        Label="to_this_table",
                    )
                )

        # add links pointing from each row of the second table to all the rows
        # of the first table and also to all the rows of the second table
        # upwards
        for j in range(len(rows[1]) - 1, 0, -1):
            # links going from the row j of the second table to all the upper
            # rows in the second table
            for i in range(j):
                self.table_element.add_link_between_rows(
                    LinkBetweenRows(
                        TABLE_NAMES[1],
                        j,
                        TABLE_NAMES[1],
                        i,
                        Importance=1,
                        Label="to_second_table",
                    )
                )

            # links going from the row j to all the rows in the first table
            for i in range(len(rows[0])):
                self.table_element.add_link_between_rows(
                    LinkBetweenRows(
                        TABLE_NAMES[1],
                        j,
                        TABLE_NAMES[0],
                        i,
                        Label="to_first_table",
                        Importance=4,
                        Color=Colors.LIGHT_BLUE,
                    )
                )
