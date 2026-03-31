"""Main screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.worker import Worker, WorkerState

from qry.context import AppContext
from qry.shared.constants import (
    MSG_HELP_MAIN,
    MSG_NO_CONNECTION,
    MSG_WELCOME_NO_CONNECTION,
    TITLE_WELCOME,
)
from qry.shared.models import QueryResult
from qry.ui.screens.screen_export import ExportScreen
from qry.ui.screens.screen_history import HistoryScreen
from qry.ui.screens.screen_snippet import SnippetScreen
from qry.ui.screens.screen_table_workbench import TableWorkbench
from qry.ui.widgets.widget_editor import SqlEditor
from qry.ui.widgets.widget_results import ResultsTable
from qry.ui.widgets.widget_sidebar import DatabaseSidebar
from qry.ui.widgets.widget_statusbar import StatusBar


class MainScreen(Widget):
    """Main application screen."""

    DEFAULT_CSS = """
    MainScreen {
        layout: grid;
        grid-size: 1;
        grid-rows: 1fr auto;
        height: 100%;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #content {
        width: 1fr;
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+p", "show_snippets", "Snippets"),
        Binding("ctrl+t", "test_connection", "Test Connection"),
        Binding("f1", "help", "Help"),
    ]

    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self._ctx = ctx
        self._query_worker: Worker | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            yield DatabaseSidebar(id="sidebar")
            with Vertical(id="content"):
                yield SqlEditor(settings=self._ctx.settings.editor, id="editor")
                yield ResultsTable(id="results")
        yield StatusBar(id="statusbar")

    def on_mount(self) -> None:
        self._update_sidebar()
        self._update_statusbar()
        self._setup_completion()
        if not self._ctx.is_connected:
            self.app.notify(
                MSG_WELCOME_NO_CONNECTION,
                title=TITLE_WELCOME,
            )

    def _setup_completion(self) -> None:
        editor = self.query_one("#editor", SqlEditor)
        if self._ctx.query_service:
            editor.set_completion_callback(self._ctx.query_service.get_completions)
            editor.set_search_callback(self._ctx.query_service.search_history)
        else:
            editor.set_completion_callback(None)
            editor.set_search_callback(None)

    def _update_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        if self._ctx.is_connected and self._ctx.adapter:
            sidebar.set_adapter(self._ctx.adapter)
            if not sidebar.has_class("visible"):
                sidebar.add_class("visible")
        else:
            sidebar.clear_adapter()

    def _update_statusbar(self) -> None:
        statusbar = self.query_one("#statusbar", StatusBar)
        if self._ctx.current_connection:
            statusbar.set_connection_info(self._ctx.current_connection)
        else:
            statusbar.clear_connection()

    def _update_query_result(self, result: QueryResult) -> None:
        statusbar = self.query_one("#statusbar", StatusBar)
        statusbar.set_query_result(result.row_count, result.execution_time_ms)

    def on_sql_editor_execute_requested(
        self,
        message: SqlEditor.ExecuteRequested,
    ) -> None:
        if not self._ctx.query_service:
            self.app.notify(MSG_NO_CONNECTION, severity="error")
            return

        # Cancel any running query
        if self._query_worker and self._query_worker.state == WorkerState.RUNNING:
            self._query_worker.cancel()

        # Show running state
        statusbar = self.query_one("#statusbar", StatusBar)
        statusbar.set_running()

        # Clear previous errors
        editor = self.query_one("#editor", SqlEditor)
        editor.clear_error()

        # Run query in background thread (non-blocking)
        query_service = self._ctx.query_service
        sql = message.query

        def _execute() -> list[QueryResult]:
            return query_service.execute_multi(sql)

        self._query_worker = self.run_worker(_execute, thread=True)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle async query completion."""
        if event.worker is not self._query_worker:
            return

        if event.state == WorkerState.SUCCESS:
            results = event.worker.result
            if not results:
                return
            self._display_results(results)
        elif event.state == WorkerState.ERROR:
            statusbar = self.query_one("#statusbar", StatusBar)
            statusbar.clear_running()
            error_msg = str(event.worker.error) if event.worker.error else "Query failed"
            self.app.notify(f"[!] {error_msg}", severity="error")
        elif event.state == WorkerState.CANCELLED:
            statusbar = self.query_one("#statusbar", StatusBar)
            statusbar.clear_running()

    def _display_results(self, results: list[QueryResult]) -> None:
        """Display query results in the results table."""
        results_table = self.query_one("#results", ResultsTable)

        if len(results) == 1:
            results_table.set_result(results[0])
            self._update_query_result(results[0])
            if results[0].error:
                editor = self.query_one("#editor", SqlEditor)
                editor.show_error(results[0].error, results[0].error_position)
        else:
            results_table.set_results(results)
            last = results[-1]
            self._update_query_result(last)
            if last.error:
                editor = self.query_one("#editor", SqlEditor)
                editor.show_error(last.error, last.error_position)

    def on_database_sidebar_table_selected(
        self,
        message: DatabaseSidebar.TableSelected,
    ) -> None:
        if self._ctx.adapter:
            self.app.push_screen(
                TableWorkbench(message.table_name, self._ctx.adapter)
            )

    def on_results_table_export_requested(
        self,
        message: ResultsTable.ExportRequested,
    ) -> None:
        def _on_export_dismiss(result: str | None) -> None:
            if result:
                statusbar = self.query_one("#statusbar", StatusBar)
                statusbar.set_message(f"Exported to {result}")

        self.app.push_screen(ExportScreen(message.result), callback=_on_export_dismiss)

    def on_sql_editor_history_requested(
        self, message: SqlEditor.HistoryRequested
    ) -> None:
        self._show_history()

    def _show_history(self) -> None:
        if not self._ctx.query_service:
            self.app.notify(MSG_NO_CONNECTION, severity="error")
            return

        entries = self._ctx.query_service.get_history(count=100)
        if not entries:
            self.app.notify("No history entries")
            return

        def _on_history_dismiss(query: str | None) -> None:
            if query:
                editor = self.query_one("#editor", SqlEditor)
                editor.set_query(query)

        self.app.push_screen(HistoryScreen(entries), callback=_on_history_dismiss)

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        sidebar.toggle()

    def action_test_connection(self) -> None:
        if self._ctx.current_connection:
            success, message = self._ctx.test_connection(self._ctx.current_connection)
            severity = "information" if success else "error"
            self.app.notify(message, title="Connection Test", severity=severity)
        else:
            self.app.notify("No active connection", severity="warning")

    def action_show_snippets(self) -> None:
        snippets = self._ctx.snippet_repository.list_all()
        if not snippets:
            self.app.notify("No snippets saved")
            return

        def _on_snippet_dismiss(query: str | None) -> None:
            if query:
                editor = self.query_one("#editor", SqlEditor)
                editor.set_query(query)

        self.app.push_screen(SnippetScreen(snippets), callback=_on_snippet_dismiss)

    def action_help(self) -> None:
        self.app.notify(MSG_HELP_MAIN)

    def refresh_connection(self) -> None:
        self._update_sidebar()
        self._update_statusbar()
        self._setup_completion()
