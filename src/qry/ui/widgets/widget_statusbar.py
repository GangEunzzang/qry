"""Status bar widget."""

from textual.widgets import Static


class StatusBar(Static):
    """Status bar showing connection and query info."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $surface;
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._connection_name: str | None = None
        self._message: str = ""

    def on_mount(self) -> None:
        self._update_display()

    def set_connection(self, name: str) -> None:
        self._connection_name = name
        self._update_display()

    def clear_connection(self) -> None:
        self._connection_name = None
        self._update_display()

    def set_message(self, message: str) -> None:
        self._message = message
        self._update_display()

    def clear_message(self) -> None:
        self._message = ""
        self._update_display()

    def _update_display(self) -> None:
        parts = []

        if self._connection_name:
            parts.append(f"[bold]{self._connection_name}[/bold]")
        else:
            parts.append("[dim]No connection[/dim]")

        if self._message:
            parts.append(self._message)

        self.update(" | ".join(parts))
