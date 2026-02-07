"""Main Textual application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from qry.context import AppContext
from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.shared.constants import AVAILABLE_THEMES
from qry.ui.screens.screen_main import MainScreen
from qry.ui.screens.screen_theme import ThemeScreen


class QryApp(App):
    """The main qry TUI application."""

    TITLE = "qry"
    SUB_TITLE = "SQL TUI Client"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "cancel", "Cancel", priority=True),
        Binding("f1", "help", "Help"),
        Binding("f2", "change_theme", "Theme"),
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
        super().__init__()
        self._initial_connection = connection
        self._ctx = ctx or AppContext.create()

    @property
    def ctx(self) -> AppContext:
        return self._ctx

    def compose(self) -> ComposeResult:
        yield Header()
        yield MainScreen(ctx=self._ctx)
        yield Footer()

    def on_mount(self) -> None:
        self._apply_theme(self._ctx.settings.theme)
        if self._initial_connection:
            self._connect(self._initial_connection)

    def _connect(self, config: ConnectionConfig) -> None:
        try:
            self._ctx.connect(config)
            self.notify(f"Connected to {config.name}")
            main_screen = self.query_one(MainScreen)
            main_screen.refresh_connection()
        except Exception as e:
            self.notify(f"Connection failed: {e}", severity="error")

    def action_quit(self) -> None:
        self._ctx.disconnect()
        self.exit()

    def action_cancel(self) -> None:
        if self._ctx.query_service and self._ctx.query_service.is_running:
            self._ctx.query_service.cancel()
            self.notify("Query cancelled")

    def action_help(self) -> None:
        self.notify(
            "Ctrl+Enter: Run query | Ctrl+B: Toggle sidebar | F2: Theme | Ctrl+Q: Quit",
            title="qry Help",
        )

    def _apply_theme(self, theme_name: str) -> None:
        if theme_name in AVAILABLE_THEMES:
            self.theme = theme_name

    def action_change_theme(self) -> None:
        def _on_theme_selected(theme_name: str | None) -> None:
            if theme_name:
                self._apply_theme(theme_name)
                self._ctx.settings.theme = theme_name
                self._ctx.settings.save()

        self.push_screen(ThemeScreen(self.theme), callback=_on_theme_selected)


def run(
    connection: ConnectionConfig | None = None,
    db_path: str | None = None,
) -> None:
    if db_path and not connection:
        connection = ConnectionConfig(
            name="cli",
            db_type=DatabaseType.SQLITE,
            path=db_path,
        )

    app = QryApp(connection=connection)
    app.run()
