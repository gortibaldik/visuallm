from dataclasses import dataclass
from enum import Enum
from typing import Any

from .element_base import ElementBase


class Colors(Enum):

    """Colors Enumeration

    TODO NOTES:
    - I want to find some standardized way how to handle css colors in python.
    - for now it is just a list of predefined css colors
    """

    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    ORANGE = "orange"
    LIGHT_BLUE = "CornflowerBlue"


@dataclass
class LinkBetweenRows:

    """Class representing all the values needed for the display of links
    between table rows in the frontend.
    """

    StartTable: str
    StartRow: int
    EndTable: str
    EndRow: int
    Importance: int
    Label: str
    Color: str

    def __init__(
        self,
        StartTable: str,
        StartRow: int,
        EndTable: str,
        EndRow: int,
        Importance: int = 3,
        Label: str = "",
        Color: Colors | str = Colors.ORANGE,
    ):
        """Args:
        ----
            StartTable (str): name of the table where the link should start
            StartRow (int): row of the start table where the link should start
            EndTable (str): name of the table where the link should end
            EndRow (int): row of the end table where the link should end
            Importance (int, optional): width of the link. Defaults to 3.
            Label (str, optional): text displayed above the link. Defaults to "".
            Color (Union[Colors, str], optional): color of the link. Defaults to Colors.RED.
        """
        self.StartTable = StartTable
        self.StartRow = StartRow
        self.EndTable = EndTable
        self.EndRow = EndRow
        self.Importance = Importance
        self.Label = Label
        self._set_color(Color)

    def _set_color(self, color):
        if isinstance(color, Colors):
            self.Color: str = color.value
        elif isinstance(color, str):
            self.Color = color
        else:
            raise TypeError(
                "Only str and Colors enum are supported for the value of "
                f"Color. ({type(color)})"
            )


class TableNameNotRegisteredError(ValueError):
    def __init__(self, start_table: str, end_table: str, tables_keys: list[str]):
        super().__init__(
            f"Invalid table name: one, or both of [{start_table},"
            f"{end_table}] not in {tables_keys}"
        )


class TableElement(ElementBase):
    def __init__(self, name="table"):
        super().__init__(name=name, type="connected_tables")
        self.clear()

    def clear(self):
        """Set all the tables, and links between rows to empty lists."""
        self.set_changed()
        self._tables: dict[str, Any] = {}
        self.tables = []
        self.links = []

    def check_rows(self, headers: list[str], rows: list[list[str]]):
        return all(len(row) == len(headers) for row in rows)

    def add_table(
        self,
        title: str,
        headers: list[str],
        rows: list[list[str]],
        prepend: bool = False,
    ):
        if not self.check_rows(headers, rows):
            raise ValueError(
                "The length of some row doesn't match the lenght of headers."
            )
        if title in self._tables:
            raise ValueError("Cannot add two tables with the same name!")
        self.set_changed()
        self._tables[title] = {"headers": headers, "rows": rows, "title": title}
        if prepend:
            self.tables = [self._tables[title]] + self.tables
        else:
            self.tables.append(self._tables[title])

    def add_link_between_rows(self, link: LinkBetweenRows):
        if (link.StartTable not in self._tables) or (link.EndTable not in self._tables):
            raise TableNameNotRegisteredError(
                link.StartTable, link.EndTable, list(self._tables.keys())
            )

        if (len(self._tables[link.StartTable]["rows"]) <= link.StartRow) or (
            len(self._tables[link.EndTable]["rows"]) <= link.EndRow
        ):
            raise ValueError(
                f"{len(self._tables[link.StartTable]['rows']), link.StartRow}"
                f"{len(self._tables[link.EndTable]['rows']), link.EndRow}"
            )
        self.set_changed()
        self.links.append(link)

    def construct_element_configuration(self):
        return {"tables": self.tables, "links": self.links}
