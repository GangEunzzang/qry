"""Custom header widget for qry."""

from rich.text import Text
from textual.widgets import Static

_LEFT = "> qry // sql tui client"
_RIGHT = "F1 info  F2 theme  ^q quit"
_MARKUP_LEFT = "[bold]> qry[/bold] [dim]// sql tui client[/dim]"
_MARKUP_RIGHT = "[dim]F1 info  F2 theme  ^q quit[/dim]"
# Plain-text widths for padding calculation
_LEFT_WIDTH = Text.from_markup(_MARKUP_LEFT).cell_len
_RIGHT_WIDTH = Text.from_markup(_MARKUP_RIGHT).cell_len


class QryHeader(Static):
    """Custom header: > qry // sql tui client."""

    DEFAULT_CSS = """
    QryHeader {
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 1;
    }
    """

    def on_mount(self) -> None:
        self._render_header()

    def on_resize(self) -> None:
        self._render_header()

    def _render_header(self) -> None:
        usable = (self.size.width or 80) - 2  # minus padding
        gap = max(1, usable - _LEFT_WIDTH - _RIGHT_WIDTH)
        self.update(f"{_MARKUP_LEFT}{' ' * gap}{_MARKUP_RIGHT}")
