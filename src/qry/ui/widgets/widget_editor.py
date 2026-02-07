"""SQL Editor widget."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Static, TextArea
from textual.widgets.text_area import Selection

from qry.domains.query.models import CompletionItem
from qry.shared.settings import EditorSettings
from qry.ui.widgets.widget_completion import CompletionDropdown
from qry.ui.widgets.widget_error_bar import ErrorBar


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
        Binding("ctrl+h", "history", "History"),
    ]

    class HistoryRequested(Message):
        pass

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
        self._completion_callback: Callable[[str, int], list[CompletionItem]] | None = None

    def compose(self) -> ComposeResult:
        yield TextArea(
            language="sql",
            theme="dracula",
            show_line_numbers=self._settings.show_line_numbers,
            tab_behavior="indent",
            id="sql-input",
        )
        yield CompletionDropdown(id="completion-dropdown")
        yield ErrorBar(id="error-bar")

    def on_mount(self) -> None:
        self._text_area = self.query_one("#sql-input", TextArea)
        self.border_title = "Query"

    def set_completion_callback(
        self, callback: Callable[[str, int], list[CompletionItem]] | None
    ) -> None:
        self._completion_callback = callback

    def _get_cursor_offset(self) -> int:
        """Convert TextArea cursor (row, col) to flat character offset."""
        if not self._text_area:
            return 0
        text = self._text_area.text
        row, col = self._text_area.cursor_location
        lines = text.split("\n")
        offset = sum(len(lines[i]) + 1 for i in range(min(row, len(lines))))
        offset += col
        return offset

    def action_execute(self) -> None:
        if self._text_area:
            self.clear_error()
            query = self._text_area.text.strip()
            if query:
                self.post_message(self.ExecuteRequested(query))

    def action_complete(self) -> None:
        if not self._text_area or not self._completion_callback:
            return
        text = self._text_area.text
        cursor_pos = self._get_cursor_offset()
        items = self._completion_callback(text, cursor_pos)
        dropdown = self.query_one("#completion-dropdown", CompletionDropdown)
        dropdown.show_completions(items)

    def _get_word_prefix_length(self) -> int:
        """Get length of the word prefix before cursor."""
        if not self._text_area:
            return 0
        row, col = self._text_area.cursor_location
        text = self._text_area.text
        lines = text.split("\n")
        if row < len(lines):
            line = lines[row]
            start = col
            while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
                start -= 1
            return col - start
        return 0

    def on_completion_dropdown_item_selected(
        self, event: CompletionDropdown.ItemSelected
    ) -> None:
        if self._text_area:
            prefix_len = self._get_word_prefix_length()
            row, col = self._text_area.cursor_location
            start_col = col - prefix_len

            start = (row, start_col)
            end = (row, col)
            self._text_area.selection = Selection(start, end)
            self._text_area.replace(event.item.text, start, end)

            new_col = start_col + len(event.item.text)
            self._text_area.cursor_location = (row, new_col)
            self._text_area.focus()

    def on_completion_dropdown_dismissed(
        self, event: CompletionDropdown.Dismissed
    ) -> None:
        if self._text_area:
            self._text_area.focus()

    def action_history(self) -> None:
        self.post_message(self.HistoryRequested())

    def set_query(self, query: str) -> None:
        if self._text_area:
            self._text_area.text = query

    def get_query(self) -> str:
        if self._text_area:
            return self._text_area.text
        return ""

    def show_error(self, message: str, position: int | None = None) -> None:
        if self._settings.inline_errors:
            error_bar = self.query_one("#error-bar", ErrorBar)
            error_bar.show_error(message, position)
        else:
            self.app.notify(f"Error: {message}", severity="error")

    def clear_error(self) -> None:
        error_bar = self.query_one("#error-bar", ErrorBar)
        error_bar.clear_error()
