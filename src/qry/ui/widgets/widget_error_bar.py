"""Inline error display bar for SQL editor."""

from textual.widgets import Static


class ErrorBar(Static):
    """Displays SQL error messages below the editor."""

    DEFAULT_CSS = """
    ErrorBar {
        height: auto;
        max-height: 3;
        background: $error 15%;
        color: $error;
        padding: 0 1;
        display: none;
    }

    ErrorBar.visible {
        display: block;
    }
    """

    def show_error(self, message: str, position: int | None = None) -> None:
        prefix = f"[Line {position}] " if position else ""
        self.update(f"\u2717 {prefix}{message}")
        self.add_class("visible")

    def clear_error(self) -> None:
        self.remove_class("visible")
        self.update("")
