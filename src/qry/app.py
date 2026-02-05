"""Main Textual application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from qry.connection.config import ConnectionConfig, DatabaseType
from qry.core.context import AppContext
from qry.settings.config import Settings
from qry.ui.screens.main import MainScreen


class QryApp(App):
    """The main qry TUI application."""

    TITLE = "qry"
    SUB_TITLE = "SQL TUI Client"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "cancel", "Cancel", priority=True),
        Binding("f1", "help", "Help"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(
        self,
        connection: ConnectionConfig | None = None,
        ctx: AppContext | None = None,
    ) -> None:
        """Initialize application.

        Args:
            connection: Initial connection to establish.
            ctx: Application context. Creates new one if not provided.
        """
        super().__init__()
        self._initial_connection = connection
        self._ctx = ctx or AppContext.create()

    @property
    def ctx(self) -> AppContext:
        """Get application context."""
        return self._ctx

    def compose(self) -> ComposeResult:
        yield Header()
        yield MainScreen(ctx=self._ctx)
        yield Footer()

    def on_mount(self) -> None:
        """Connect to database on mount if connection provided."""
        if self._initial_connection:
            self._connect(self._initial_connection)

    def _connect(self, config: ConnectionConfig) -> None:
        """Connect to database."""
        try:
            self._ctx.connect(config)
            self.notify(f"Connected to {config.name}")

            # Refresh main screen
            main_screen = self.query_one(MainScreen)
            main_screen.refresh_connection()
        except Exception as e:
            self.notify(f"Connection failed: {e}", severity="error")

    def action_quit(self) -> None:
        """Quit the application."""
        self._ctx.disconnect()
        self.exit()

    def action_cancel(self) -> None:
        """Cancel current operation."""
        if self._ctx.query_service:
            self._ctx.query_service.cancel()
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
        db_path: Path to SQLite database (shortcut for quick access).
    """
    if db_path and not connection:
        connection = ConnectionConfig(
            name="cli",
            db_type=DatabaseType.SQLITE,
            path=db_path,
        )

    app = QryApp(connection=connection)
    app.run()
