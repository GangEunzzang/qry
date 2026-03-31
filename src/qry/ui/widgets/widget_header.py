"""Custom header widget for qry."""

from textual.widgets import Static


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
        width = self.size.width or 80
        left = "[bold]> qry[/bold] [dim]// sql tui client[/dim]"
        right = "[dim]F1 info  F2 theme  ^q quit[/dim]"
        self.update(f"{left}{' ' * max(1, width - 42)}{right}")

    def on_resize(self) -> None:
        self.on_mount()
