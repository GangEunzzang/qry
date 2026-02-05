"""SQL Editor widget."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Static, TextArea

from qry.settings.settings_config import EditorSettings


class SqlEditor(Static):
    """SQL editor widget with syntax highlighting."""

    DEFAULT_CSS = """
    SqlEditor {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
    }

    SqlEditor:focus-within {
        border: solid $accent;
    }

    SqlEditor TextArea {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+enter", "execute", "Run Query", priority=True),
        Binding("ctrl+space", "complete", "Complete"),
    ]

    class ExecuteRequested(Message):
        def __init__(self, query: str) -> None:
            super().__init__()
            self.query = query

    def __init__(
        self,
        settings: EditorSettings | None = None,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._settings = settings or EditorSettings()
        self._text_area: TextArea | None = None

    def compose(self) -> ComposeResult:
        yield TextArea(
            language="sql",
            theme="dracula",
            show_line_numbers=self._settings.show_line_numbers,
            tab_behavior="indent",
            id="sql-input",
        )

    def on_mount(self) -> None:
        self._text_area = self.query_one("#sql-input", TextArea)
        self.border_title = "Query"

    def action_execute(self) -> None:
        if self._text_area:
            query = self._text_area.text.strip()
            if query:
                self.post_message(self.ExecuteRequested(query))

    def action_complete(self) -> None:
        self.app.notify("Autocompletion not yet implemented")

    def set_query(self, query: str) -> None:
        if self._text_area:
            self._text_area.text = query

    def get_query(self) -> str:
        if self._text_area:
            return self._text_area.text
        return ""

    def show_error(self, message: str, position: int | None = None) -> None:
        # TODO: Implement inline error display
        self.app.notify(f"Error: {message}", severity="error")
