"""Main Textual application."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from qry.connection.config import ConnectionConfig, DatabaseType
from qry.database.base import DatabaseAdapter
from qry.database.sqlite import SQLiteAdapter
from qry.settings.config import Settings
from qry.ui.screens.main import MainScreen


class QryApp(App):
    """The main qry TUI application."""

    TITLE = "qry"
    SUB_TITLE = "SQL TUI Client"
    CSS_PATH = "ui/themes/dark.tcss"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "cancel", "Cancel", priority=True),
        Binding("f1", "help", "Help"),
    ]

    def __init__(
        self,
        connection: ConnectionConfig | None = None,
        settings: Settings | None = None,
    ) -> None:
        super().__init__()
        self._connection = connection
        self._settings = settings or Settings.load()
        self._adapter: DatabaseAdapter | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield MainScreen(adapter=self._adapter, settings=self._settings)
        yield Footer()

    def on_mount(self) -> None:
        if self._connection:
            self._connect(self._connection)

    def _connect(self, config: ConnectionConfig) -> None:
        """Connect to database.

        Args:
            config: Connection configuration.
        """
        try:
            adapter = self._create_adapter(config)
            adapter.connect()
            self._adapter = adapter

            main_screen = self.query_one(MainScreen)
            main_screen.set_adapter(adapter)

            self.notify(f"Connected to {config.name}")
        except Exception as e:
            self.notify(f"Connection failed: {e}", severity="error")

    def _create_adapter(self, config: ConnectionConfig) -> DatabaseAdapter:
        """Create database adapter for config.

        Args:
            config: Connection configuration.

        Returns:
            Database adapter instance.
        """
        if config.db_type == DatabaseType.SQLITE:
            if not config.path:
                raise ValueError("SQLite requires path")
            return SQLiteAdapter(config.path)

        raise ValueError(f"Unsupported database type: {config.db_type}")

    def action_quit(self) -> None:
        """Quit the application."""
        if self._adapter:
            self._adapter.disconnect()
        self.exit()

    def action_cancel(self) -> None:
        """Cancel current operation."""
        if self._adapter:
            self._adapter.cancel()
        self.exit()

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Ctrl+Enter: Run query | Ctrl+B: Toggle sidebar | Ctrl+Q: Quit",
            title="qry Help",
        )


def run(
    connection: ConnectionConfig | None = None,
    db_path: str | None = None,
) -> None:
    """Run the qry application.

    Args:
        connection: Connection configuration.
        db_path: Path to SQLite database (shortcut).
    """
    if db_path and not connection:
        connection = ConnectionConfig(
            name="cli",
            db_type=DatabaseType.SQLITE,
            path=db_path,
        )

    app = QryApp(connection=connection)
    app.run()
