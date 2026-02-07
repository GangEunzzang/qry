"""Autocompletion dropdown widget."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from qry.domains.query.models import CompletionItem


class CompletionDropdown(Widget):
    """Dropdown widget showing autocompletion suggestions."""

    DEFAULT_CSS = """
    CompletionDropdown {
        layer: overlay;
        width: 40;
        max-height: 10;
        border: solid $accent;
        background: $surface;
        display: none;
    }

    CompletionDropdown.visible {
        display: block;
    }

    CompletionDropdown OptionList {
        height: auto;
        max-height: 10;
        scrollbar-size: 1 1;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Dismiss", priority=True),
        Binding("enter", "select", "Select", priority=True),
    ]

    KIND_ICONS: ClassVar[dict[str, str]] = {
        "table": "[T]",
        "column": "[C]",
        "keyword": "[K]",
    }

    class ItemSelected(Message):
        def __init__(self, item: CompletionItem) -> None:
            super().__init__()
            self.item = item

    class Dismissed(Message):
        pass

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._items: list[CompletionItem] = []
        self._option_list: OptionList | None = None

    def compose(self) -> ComposeResult:
        yield OptionList(id="completion-list")

    def on_mount(self) -> None:
        self._option_list = self.query_one("#completion-list", OptionList)

    def show_completions(self, items: list[CompletionItem]) -> None:
        self._items = items
        if not items:
            self.hide()
            return

        if self._option_list:
            self._option_list.clear_options()
            for item in items:
                kind_icon = self.KIND_ICONS.get(item.kind, "[ ]")
                label = f"{kind_icon} {item.text}"
                if item.detail:
                    label += f"  ({item.detail})"
                self._option_list.add_option(Option(label, id=item.text))

            if items:
                self._option_list.highlighted = 0

        self.add_class("visible")
        self.focus()

    def hide(self) -> None:
        self.remove_class("visible")
        self._items = []

    @property
    def is_visible(self) -> bool:
        return self.has_class("visible")

    def action_dismiss(self) -> None:
        self.hide()
        self.post_message(self.Dismissed())

    def action_select(self) -> None:
        if self._option_list and self._items:
            idx = self._option_list.highlighted
            if idx is not None and 0 <= idx < len(self._items):
                self.post_message(self.ItemSelected(self._items[idx]))
                self.hide()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        idx = event.option_index
        if 0 <= idx < len(self._items):
            self.post_message(self.ItemSelected(self._items[idx]))
            self.hide()
