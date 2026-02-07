"""History screen for query re-execution."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from qry.domains.query.models import HistoryEntry


class HistoryScreen(ModalScreen[str | None]):
    """Modal screen showing query history for re-execution."""

    DEFAULT_CSS = """
    HistoryScreen {
        align: center middle;
    }

    #history-dialog {
        width: 80;
        max-height: 30;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #history-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #history-search {
        margin-bottom: 1;
    }

    #history-list {
        height: 1fr;
        min-height: 10;
        max-height: 20;
    }

    #history-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, entries: list[HistoryEntry]) -> None:
        super().__init__()
        self._entries = entries
        self._filtered: list[HistoryEntry] = list(entries)

    def compose(self) -> ComposeResult:
        with Vertical(id="history-dialog"):
            yield Label("Query History", id="history-title")
            yield Input(placeholder="Search queries...", id="history-search")
            yield OptionList(id="history-list")
            yield Static("Enter: Execute | Escape: Cancel", id="history-hint")

    def on_mount(self) -> None:
        self._refresh_list()
        self.query_one("#history-search", Input).focus()

    def _refresh_list(self) -> None:
        option_list = self.query_one("#history-list", OptionList)
        option_list.clear_options()
        for entry in self._filtered:
            ts = entry.timestamp.strftime("%m/%d %H:%M")
            conn = f" [{entry.connection_name}]" if entry.connection_name else ""
            query_preview = entry.query[:60].replace("\n", " ")
            if len(entry.query) > 60:
                query_preview += "..."
            label = f"{ts}{conn}  {query_preview}"
            option_list.add_option(Option(label))
        if self._filtered:
            option_list.highlighted = 0
        else:
            option_list.add_option(Option("No matching queries", disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        pattern = event.value.strip()
        if pattern:
            pattern_lower = pattern.lower()
            self._filtered = [
                e for e in self._entries if pattern_lower in e.query.lower()
            ]
        else:
            self._filtered = list(self._entries)
        self._refresh_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        option_list = self.query_one("#history-list", OptionList)
        highlighted = option_list.highlighted
        if highlighted is not None and 0 <= highlighted < len(self._filtered):
            self.dismiss(self._filtered[highlighted].query)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx].query)

    def action_cancel(self) -> None:
        self.dismiss(None)
