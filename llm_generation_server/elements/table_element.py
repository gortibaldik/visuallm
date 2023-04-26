from dataclasses import dataclass
from typing import List

from .element_base import ElementBase, ElementDescription


@dataclass
class LinkBetweenRows:
    StartTable: str
    StartId: int
    EndTable: str
    EndId: int
    Importance: int
    Label: str


class TableElement(ElementBase):
    def __init__(self, name="table"):
        super().__init__(name=name)
        self.clear()

    def clear(self):
        self.changed = True
        self._tables = {}
        self.tables = []
        self.links = []

    def check_rows(self, headers: List[str], rows: List[List[str]]):
        for row in rows:
            if len(row) != len(headers):
                return False
        return True

    def add_table(self, title: str, headers: List[str], rows: List[List[str]]):
        if not self.check_rows(headers, rows):
            raise ValueError()
        self.changed = True
        self._tables[title] = dict(headers=headers, rows=rows, title=title)
        self.tables.append(self._tables[title])

    def add_link_between_rows(
        self,
        start_table: str,
        start_row: int,
        end_table: str,
        end_row: int,
        importance: int,
        label: str,
    ):
        if (start_table not in self._tables) or (end_table not in self._tables):
            raise ValueError()
        if (len(self._tables[start_table]["rows"]) <= start_row) or (
            len(self._tables[end_table]["rows"]) <= end_row
        ):
            raise ValueError(
                f"{len(self._tables[start_table]['rows']), start_row}"
                + f"{len(self._tables[end_table]['rows']), end_row}"
            )
        self.changed = True
        self.links.append(
            LinkBetweenRows(
                start_table, start_row, end_table, end_row, importance, label
            )
        )

    def construct_element_description(self):
        self.changed = False
        return ElementDescription(
            name=self.name,
            type="connected_tables",
            configuration=dict(tables=self.tables, links=self.links),
        )

    def add_endpoint(self, app):
        pass
