"""Results table widget."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import DataTable, Static

from qry.domains.query.models import QueryResult


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
    ]

    class ExportRequested(Message):
        def __init__(self, result: QueryResult) -> None:
            super().__init__()
            self.result = result

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._result: QueryResult | None = None
        self._table: DataTable | None = None

    def compose(self) -> ComposeResult:
        yield DataTable(id="results-table")

    def on_mount(self) -> None:
        self._table = self.query_one("#results-table", DataTable)
        self._table.cursor_type = "row"
        self.border_title = "Results"

    def set_result(self, result: QueryResult) -> None:
        self._result = result

        if not self._table:
            return

        self._table.clear(columns=True)

        if result.error:
            self._table.add_column("Error")
            self._table.add_row(result.error)
            self.border_title = "Results - Error"
            return

        if not result.columns:
            self.border_title = f"Results - {result.row_count} rows affected"
            return

        for col in result.columns:
            self._table.add_column(col)

        for row in result.rows:
            self._table.add_row(*[str(v) if v is not None else "NULL" for v in row])

        self.border_title = f"Results - {result.row_count} rows ({result.execution_time_ms:.1f}ms)"

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

    def action_copy(self) -> None:
        self.app.notify("Copy not yet implemented")
