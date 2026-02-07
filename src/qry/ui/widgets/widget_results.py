"""Results table widget."""

import json
from enum import Enum

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable, Static

from qry.domains.query.models import QueryResult


class SortDirection(Enum):
    NONE = "none"
    ASC = "asc"
    DESC = "desc"


class ResultsTable(Static):
    """Widget for displaying query results."""

    DEFAULT_CSS = """
    ResultsTable {
        height: 2fr;
        border: solid $primary;
    }

    ResultsTable:focus-within {
        border: solid $accent;
    }

    ResultsTable DataTable {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+e", "export", "Export"),
        Binding("ctrl+c", "copy", "Copy"),
        Binding("enter", "copy_cell", "Copy Cell"),
        Binding("s", "toggle_sort", "Sort"),
    ]

    class ExportRequested(Message):
        def __init__(self, result: QueryResult) -> None:
            super().__init__()
            self.result = result

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._result: QueryResult | None = None
        self._table: DataTable | None = None
        self._sort_column: int | None = None
        self._sort_direction: SortDirection = SortDirection.NONE

    def compose(self) -> ComposeResult:
        yield DataTable(id="results-table")

    def on_mount(self) -> None:
        self._table = self.query_one("#results-table", DataTable)
        self._table.cursor_type = "cell"
        self.border_title = "Results"

    def set_result(self, result: QueryResult) -> None:
        self._result = result
        self._sort_column = None
        self._sort_direction = SortDirection.NONE

        if not self._table:
            return

        self._render_table()

    def _render_table(self) -> None:
        """Render the DataTable with current result and sort state."""
        if not self._table or not self._result:
            return

        result = self._result
        self._table.clear(columns=True)

        if result.error:
            self._table.add_column("Error")
            self._table.add_row(result.error)
            self.border_title = "Results - Error"
            return

        if not result.columns:
            self.border_title = f"Results - {result.row_count} rows affected"
            return

        for i, col in enumerate(result.columns):
            label = self._column_label(col, i)
            self._table.add_column(label)

        rows = self._sorted_rows()
        for row in rows:
            self._table.add_row(*[str(v) if v is not None else "NULL" for v in row])

        self.border_title = f"Results - {result.row_count} rows ({result.execution_time_ms:.1f}ms)"

    def _column_label(self, name: str, index: int) -> str:
        """Return column label with sort indicator if applicable."""
        if self._sort_column == index:
            if self._sort_direction == SortDirection.ASC:
                return f"{name} \u25b2"
            if self._sort_direction == SortDirection.DESC:
                return f"{name} \u25bc"
        return name

    def _sorted_rows(self) -> list[tuple]:
        """Return rows sorted by current sort state."""
        if not self._result:
            return []
        rows = list(self._result.rows)
        if (
            self._sort_column is None
            or self._sort_direction == SortDirection.NONE
        ):
            return rows

        col_idx = self._sort_column
        reverse = self._sort_direction == SortDirection.DESC

        def sort_key(row: tuple) -> tuple:
            val = row[col_idx]
            if val is None:
                return (1, "")
            return (0, val)

        try:
            rows.sort(key=sort_key, reverse=reverse)
        except TypeError:
            def safe_sort_key(row: tuple) -> tuple:
                val = row[col_idx]
                if val is None:
                    return (1, "")
                return (0, str(val))
            rows.sort(key=safe_sort_key, reverse=reverse)
        return rows

    def set_results(self, results: list[QueryResult]) -> None:
        """Display multiple query results (shows last successful result with summary)."""
        if not results:
            return

        display_result = results[-1]
        for r in reversed(results):
            if r.columns:
                display_result = r
                break

        self.set_result(display_result)

        total = len(results)
        success = sum(1 for r in results if r.is_success)
        if total > 1:
            total_time = sum(r.execution_time_ms for r in results)
            last_result = results[-1]
            if last_result.error:
                error_msg = f"Error in query {success + 1}"
                self.border_title = (
                    f"Results - {success}/{total} queries"
                    f" ({total_time:.1f}ms) - {error_msg}"
                )
            else:
                self.border_title = (
                    f"Results - {total} queries ({total_time:.1f}ms)"
                )

    def action_export(self) -> None:
        if self._result:
            self.post_message(self.ExportRequested(self._result))

    def action_toggle_sort(self) -> None:
        """Toggle sort on the current column: NONE -> ASC -> DESC -> NONE."""
        if not self._result or not self._table or not self._result.columns:
            return

        col_idx = self._table.cursor_column
        if col_idx is None or col_idx < 0 or col_idx >= len(self._result.columns):
            return

        if self._sort_column == col_idx:
            # Cycle direction on same column
            if self._sort_direction == SortDirection.NONE:
                self._sort_direction = SortDirection.ASC
            elif self._sort_direction == SortDirection.ASC:
                self._sort_direction = SortDirection.DESC
            else:
                self._sort_direction = SortDirection.NONE
                self._sort_column = None
        else:
            # New column: start with ASC
            self._sort_column = col_idx
            self._sort_direction = SortDirection.ASC

        self._render_table()

    def _get_row_as_json(self, row_index: int) -> str | None:
        """Get a row as a JSON string."""
        if not self._result:
            return None
        if row_index < 0 or row_index >= len(self._result.rows):
            return None
        row_data = self._result.rows[row_index]
        row_dict = {}
        for i, col in enumerate(self._result.columns):
            value = row_data[i] if i < len(row_data) else None
            row_dict[col] = value
        return json.dumps(row_dict, ensure_ascii=False, default=str)

    def _get_cell_value(self, row: int, col: int) -> str | None:
        """Get a cell value as a string."""
        if not self._result:
            return None
        if row < 0 or row >= len(self._result.rows):
            return None
        if col < 0 or col >= len(self._result.columns):
            return None
        value = self._result.rows[row][col]
        return str(value) if value is not None else "NULL"

    def action_copy(self) -> None:
        """Copy current row as JSON to clipboard."""
        if not self._result or not self._table:
            return
        cursor_row = self._table.cursor_row
        if cursor_row is None:
            return
        json_str = self._get_row_as_json(cursor_row)
        if json_str is None:
            return
        self.app.copy_to_clipboard(json_str)
        self.app.notify(f"Row {cursor_row + 1} copied to clipboard")

    def action_copy_cell(self) -> None:
        """Copy current cell value to clipboard."""
        if not self._result or not self._table:
            return
        cursor_row = self._table.cursor_row
        cursor_col = self._table.cursor_column
        if cursor_row is None or cursor_col is None:
            return
        text = self._get_cell_value(cursor_row, cursor_col)
        if text is None:
            return
        self.app.copy_to_clipboard(text)
        col_name = self._result.columns[cursor_col]
        self.app.notify(f"Copied: {col_name} = {text}")
