"""Reverse incremental search bar for query history (pgcli-style Ctrl+R)."""

from collections.abc import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Input, Static

from qry.domains.query.models import HistoryEntry


class ReverseSearchBar(Static):
    """Inline search bar for reverse-i-search through query history.

    Shows a prompt like "reverse-i-search: <pattern>" and displays
    matching history entries. Ctrl+R cycles through matches.
    """

    DEFAULT_CSS = """
    ReverseSearchBar {
        height: auto;
        background: $surface;
        display: none;
    }

    ReverseSearchBar.visible {
        display: block;
    }

    ReverseSearchBar #search-preview {
        height: auto;
        max-height: 3;
        color: $text-muted;
        padding: 0 1;
    }

    ReverseSearchBar #search-input {
        height: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", priority=True),
        Binding("ctrl+r", "next_match", "Next Match", priority=True),
    ]

    class Accepted(Message):
        """Emitted when a match is accepted (Enter)."""

        def __init__(self, query: str) -> None:
            super().__init__()
            self.query = query

    class Cancelled(Message):
        """Emitted when the search is cancelled (Escape)."""

        pass

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._search_callback: Callable[[str, int], list[HistoryEntry]] | None = None
        self._matches: list[HistoryEntry] = []
        self._match_index: int = 0
        self._input: Input | None = None
        self._preview: Static | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id="search-preview")
        yield Input(placeholder="reverse-i-search: ", id="search-input")

    def on_mount(self) -> None:
        self._input = self.query_one("#search-input", Input)
        self._preview = self.query_one("#search-preview", Static)

    def set_search_callback(
        self, callback: Callable[[str, int], list[HistoryEntry]] | None
    ) -> None:
        self._search_callback = callback

    def open(self) -> None:
        """Show the search bar and focus the input."""
        self._matches = []
        self._match_index = 0
        if self._input:
            self._input.value = ""
        if self._preview:
            self._preview.update("")
        self.add_class("visible")
        if self._input:
            self._input.focus()

    def close(self) -> None:
        """Hide the search bar."""
        self.remove_class("visible")
        self._matches = []
        self._match_index = 0

    @property
    def is_visible(self) -> bool:
        return self.has_class("visible")

    @property
    def current_match(self) -> str | None:
        """Return the currently highlighted match query, if any."""
        if self._matches and 0 <= self._match_index < len(self._matches):
            return self._matches[self._match_index].query
        return None

    def _do_search(self, pattern: str) -> None:
        """Execute the search and update preview."""
        if not pattern or not self._search_callback:
            self._matches = []
            self._match_index = 0
            if self._preview:
                self._preview.update("")
            return

        self._matches = self._search_callback(pattern, 50)
        self._match_index = 0
        self._update_preview()

    def _update_preview(self) -> None:
        """Update the preview label with the current match."""
        if not self._preview:
            return

        if self._matches and 0 <= self._match_index < len(self._matches):
            query = self._matches[self._match_index].query
            preview = query.replace("\n", " ")
            if len(preview) > 120:
                preview = preview[:117] + "..."
            match_info = f"({self._match_index + 1}/{len(self._matches)})"
            self._preview.update(f"{match_info} {preview}")
        elif self._input and self._input.value:
            self._preview.update("(no match)")
        else:
            self._preview.update("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._do_search(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self._accept()

    def _accept(self) -> None:
        """Accept the current match."""
        match = self.current_match
        self.close()
        if match:
            self.post_message(self.Accepted(match))
        else:
            self.post_message(self.Cancelled())

    def action_cancel(self) -> None:
        self.close()
        self.post_message(self.Cancelled())

    def action_next_match(self) -> None:
        """Cycle to the next match in history."""
        if self._matches and len(self._matches) > 1:
            self._match_index = (self._match_index + 1) % len(self._matches)
            self._update_preview()
