from typing import List
from dataclasses import dataclass

@dataclass
class RowConnection:
    StartTable: str
    StartId: int
    EndTable: str
    EndId: int
    Importance: int
    Label: str

class TableFormatter:

    def __init__(self):
        self._tables = {}
        self.tables = []
        self.connections = []
        
    def check_rows(self, headers: List[str], rows: List[List[str]]):
        for row in rows:
            if len(row) != len(headers):
                return False
        return True

    def add_table(self, title: str, headers: List[str], rows: List[List[str]]):
        if not self.check_rows(headers, rows):
            raise ValueError()
        self._tables[title] = dict(
            headers=headers,
            rows=rows,
            title=title
        )
        self.tables.append(self._tables[title])

    def add_connection(self, start_table: str, start_row: int, end_table: str, end_row: int, importance: int, label: str):
        if (start_table not in self._tables) or (end_table not in self._tables):
            raise ValueError()
        if (len(self._tables[start_table]['rows']) <= start_row) or (len(self._tables[end_table]["rows"]) <= end_row):
            raise ValueError(
                f"{len(self._tables[start_table]['rows']), start_row}" 
                + f"{len(self._tables[end_table]['rows']), end_row}"
            )
        
        self.connections.append(
            RowConnection(
                start_table,
                start_row,
                end_table,
                end_row,
                importance,
                label
            )
        )
