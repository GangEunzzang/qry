"""Main screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from qry.context import AppContext
from qry.ui.screens.screen_export import ExportScreen
from qry.ui.screens.screen_history import HistoryScreen
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
        Binding("f1", "help", "Help"),
    ]

    def __init__(self, ctx: AppContext) -> None:
        super().__init__()
        self._ctx = ctx

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

    def _setup_completion(self) -> None:
        editor = self.query_one("#editor", SqlEditor)
        if self._ctx.query_service:
            editor.set_completion_callback(self._ctx.query_service.get_completions)
        else:
            editor.set_completion_callback(None)

    def _update_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        if self._ctx.is_connected and self._ctx.adapter:
            sidebar.set_adapter(self._ctx.adapter)
        else:
            sidebar.clear_adapter()

    def _update_statusbar(self) -> None:
        statusbar = self.query_one("#statusbar", StatusBar)
        if self._ctx.current_connection:
            statusbar.set_connection(self._ctx.current_connection.name)
        else:
            statusbar.clear_connection()

    def on_sql_editor_execute_requested(
        self,
        message: SqlEditor.ExecuteRequested,
    ) -> None:
        if not self._ctx.query_service:
            self.app.notify("No database connection", severity="error")
            return

        results = self._ctx.query_service.execute_multi(message.query)
        results_table = self.query_one("#results", ResultsTable)

        if len(results) == 1:
            results_table.set_result(results[0])
            if results[0].error:
                editor = self.query_one("#editor", SqlEditor)
                editor.show_error(results[0].error, results[0].error_position)
        else:
            results_table.set_results(results)
            last = results[-1]
            if last.error:
                editor = self.query_one("#editor", SqlEditor)
                editor.show_error(last.error, last.error_position)

    def on_database_sidebar_table_selected(
        self,
        message: DatabaseSidebar.TableSelected,
    ) -> None:
        editor = self.query_one("#editor", SqlEditor)
        safe_name = message.table_name.replace('"', '""')
        editor.set_query(f'SELECT * FROM "{safe_name}" LIMIT 100;')

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
            self.app.notify("No database connection", severity="error")
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

    def action_help(self) -> None:
        self.app.notify("Press Ctrl+Enter to run query, Ctrl+B for sidebar")

    def refresh_connection(self) -> None:
        self._update_sidebar()
        self._update_statusbar()
        self._setup_completion()
