"""Theme picker screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option

from qry.shared.constants import AVAILABLE_THEMES


class ThemeScreen(ModalScreen[str | None]):
    """Modal screen for selecting a theme."""

    DEFAULT_CSS = """
    ThemeScreen {
        align: center middle;
    }

    #theme-dialog {
        width: 40;
        height: auto;
        max-height: 80%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    #theme-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #theme-list {
        height: auto;
        max-height: 20;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, current_theme: str = "") -> None:
        super().__init__()
        self._current_theme = current_theme

    def compose(self) -> ComposeResult:
        with Vertical(id="theme-dialog"):
            yield Label("Select Theme", id="theme-title")
            option_list = OptionList(id="theme-list")
            for theme_name in AVAILABLE_THEMES:
                label = f"  {theme_name}"
                if theme_name == self._current_theme:
                    label = f"* {theme_name}"
                option_list.add_option(Option(label, id=theme_name))
            yield option_list

    def on_mount(self) -> None:
        option_list = self.query_one("#theme-list", OptionList)
        if self._current_theme in AVAILABLE_THEMES:
            idx = AVAILABLE_THEMES.index(self._current_theme)
            option_list.highlighted = idx

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option_id))

    def action_cancel(self) -> None:
        self.dismiss(None)
