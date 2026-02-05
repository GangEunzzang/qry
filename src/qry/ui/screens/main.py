"""Main screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen

from qry.database.base import DatabaseAdapter
from qry.query.executor import QueryExecutor
from qry.query.history import HistoryManager
from qry.settings.config import Settings
from qry.ui.widgets.editor import SqlEditor
from qry.ui.widgets.results import ResultsTable
from qry.ui.widgets.sidebar import DatabaseSidebar
from qry.ui.widgets.statusbar import StatusBar


class MainScreen(Screen):
    """Main application screen."""

    DEFAULT_CSS = """
    MainScreen {
        layout: grid;
        grid-size: 1;
        grid-rows: 1fr auto;
    }

    #main-container {
        layout: horizontal;
    }

    #content {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar"),
        Binding("f1", "help", "Help"),
    ]

    def __init__(
        self,
        adapter: DatabaseAdapter | None = None,
        settings: Settings | None = None,
    ) -> None:
        super().__init__()
        self._adapter = adapter
        self._settings = settings or Settings()
        self._executor: QueryExecutor | None = None
        self._history = HistoryManager(max_entries=self._settings.history.max_entries)

        if adapter:
            self._executor = QueryExecutor(adapter, self._history)

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            yield DatabaseSidebar(id="sidebar")
            with Vertical(id="content"):
                yield SqlEditor(settings=self._settings.editor, id="editor")
                yield ResultsTable(id="results")
        yield StatusBar(id="statusbar")

    def on_mount(self) -> None:
        if self._adapter:
            sidebar = self.query_one("#sidebar", DatabaseSidebar)
            sidebar.set_adapter(self._adapter)

    def on_sql_editor_execute_requested(
        self,
        message: SqlEditor.ExecuteRequested,
    ) -> None:
        """Handle query execution request."""
        if not self._executor:
            self.app.notify("No database connection", severity="error")
            return

        result = self._executor.execute(message.query)
        results_table = self.query_one("#results", ResultsTable)
        results_table.set_result(result)

        if result.error:
            editor = self.query_one("#editor", SqlEditor)
            editor.show_error(result.error, result.error_position)

    def on_database_sidebar_table_selected(
        self,
        message: DatabaseSidebar.TableSelected,
    ) -> None:
        """Handle table selection from sidebar."""
        editor = self.query_one("#editor", SqlEditor)
        editor.set_query(f"SELECT * FROM {message.table_name} LIMIT 100;")

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        sidebar.toggle()

    def action_help(self) -> None:
        """Show help."""
        self.app.notify("Press Ctrl+Enter to run query, Ctrl+B for sidebar")

    def set_adapter(self, adapter: DatabaseAdapter) -> None:
        """Set database adapter.

        Args:
            adapter: Database adapter.
        """
        self._adapter = adapter
        self._executor = QueryExecutor(adapter, self._history)

        sidebar = self.query_one("#sidebar", DatabaseSidebar)
        sidebar.set_adapter(adapter)
