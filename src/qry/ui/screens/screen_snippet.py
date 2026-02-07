"""Snippet picker screen for selecting SQL snippets."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from qry.domains.snippet.models import Snippet


class SnippetScreen(ModalScreen[str | None]):
    """Modal screen listing snippets for selection."""

    DEFAULT_CSS = """
    SnippetScreen {
        align: center middle;
    }

    #snippet-dialog {
        width: 80;
        max-height: 30;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #snippet-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #snippet-search {
        margin-bottom: 1;
    }

    #snippet-list {
        height: 1fr;
        min-height: 10;
        max-height: 20;
    }

    #snippet-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, snippets: list[Snippet]) -> None:
        super().__init__()
        self._snippets = snippets
        self._filtered: list[Snippet] = list(snippets)

    def compose(self) -> ComposeResult:
        with Vertical(id="snippet-dialog"):
            yield Label("Snippets", id="snippet-title")
            yield Input(placeholder="Search snippets...", id="snippet-search")
            yield OptionList(id="snippet-list")
            yield Static("Enter: Select | Escape: Cancel", id="snippet-hint")

    def on_mount(self) -> None:
        self._refresh_list()
        self.query_one("#snippet-search", Input).focus()

    @staticmethod
    def _format_snippet_label(snippet: Snippet) -> str:
        """Build display label from a Snippet."""
        category = f"[{snippet.category}] " if snippet.category else ""
        desc = f" - {snippet.description}" if snippet.description else ""
        return f"{category}{snippet.name}{desc}"

    def _refresh_list(self) -> None:
        option_list = self.query_one("#snippet-list", OptionList)
        option_list.clear_options()
        for snippet in self._filtered:
            label = self._format_snippet_label(snippet)
            option_list.add_option(Option(label))
        if self._filtered:
            option_list.highlighted = 0
        else:
            option_list.add_option(Option("No matching snippets", disabled=True))

    def on_input_changed(self, event: Input.Changed) -> None:
        pattern = event.value.strip().lower()
        if pattern:
            self._filtered = [
                s
                for s in self._snippets
                if pattern in s.name.lower()
                or pattern in s.description.lower()
                or pattern in s.category.lower()
                or pattern in s.query.lower()
            ]
        else:
            self._filtered = list(self._snippets)
        self._refresh_list()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        option_list = self.query_one("#snippet-list", OptionList)
        highlighted = option_list.highlighted
        if highlighted is not None and 0 <= highlighted < len(self._filtered):
            self.dismiss(self._filtered[highlighted].query)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if 0 <= idx < len(self._filtered):
            self.dismiss(self._filtered[idx].query)

    def action_cancel(self) -> None:
        self.dismiss(None)
