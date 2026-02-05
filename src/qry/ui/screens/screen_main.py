"""Main screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from qry.core.core_context import AppContext
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

    def _update_sidebar(self) -> None:
        if self._ctx.is_connected and self._ctx.adapter:
            sidebar = self.query_one("#sidebar", DatabaseSidebar)
            sidebar.set_adapter(self._ctx.adapter)

    def _update_statusbar(self) -> None:
        statusbar = self.query_one("#statusbar", StatusBar)
        if self._ctx.current_connection:
            statusbar.set_connection(self._ctx.current_connection.name)

    def on_sql_editor_execute_requested(
        self,
        message: SqlEditor.ExecuteRequested,
    ) -> None:
        if not self._ctx.query_service:
            self.app.notify("No database connection", severity="error")
            return

        result = self._ctx.query_service.execute(message.query)
        results_table = self.query_one("#results", ResultsTable)
        results_table.set_result(result)

        if result.error:
            editor = self.query_one("#editor", SqlEditor)
            editor.show_error(result.error, result.error_position)

    def on_database_sidebar_table_selected(
        self,
        message: DatabaseSidebar.TableSelected,
    ) -> None:
        editor = self.query_one("#editor", SqlEditor)
        editor.set_query(f"SELECT * FROM {message.table_name} LIMIT 100;")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        sidebar.toggle()

    def action_help(self) -> None:
        self.app.notify("Press Ctrl+Enter to run query, Ctrl+B for sidebar")

    def refresh_connection(self) -> None:
        self._update_sidebar()
        self._update_statusbar()
