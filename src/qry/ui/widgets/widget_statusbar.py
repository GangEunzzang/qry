"""Status bar widget."""

from __future__ import annotations

from rich.markup import escape
from textual.widgets import Static

from qry.domains.connection.models import ConnectionConfig, DatabaseType

DB_TYPE_ICONS: dict[DatabaseType, str] = {
    DatabaseType.POSTGRES: "[pg]",
    DatabaseType.MYSQL: "[my]",
    DatabaseType.SQLITE: "[sqlite]",
}


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
        self._connection_info: str | None = None
        self._row_count: int | None = None
        self._elapsed_ms: float | None = None
        self._message: str = ""

    def on_mount(self) -> None:
        self._update_display()

    def set_connection(self, name: str) -> None:
        self._connection_name = name
        self._update_display()

    def set_connection_info(self, config: ConnectionConfig) -> None:
        icon = DB_TYPE_ICONS.get(config.db_type, "")
        if config.db_type == DatabaseType.SQLITE:
            path = escape(config.path or ":memory:")
            self._connection_info = f"{icon} {path}"
        else:
            host = escape(config.host or "localhost")
            port_str = f":{config.port}" if config.port else ""
            db = escape(config.database or "")
            self._connection_info = f"{icon} {host}{port_str}/{db}"
        self._connection_name = config.name
        self._row_count = None
        self._elapsed_ms = None
        self._update_display()

    def set_query_result(self, row_count: int, elapsed_ms: float) -> None:
        self._row_count = row_count
        self._elapsed_ms = elapsed_ms
        self._update_display()

    def clear_connection(self) -> None:
        self._connection_name = None
        self._connection_info = None
        self._row_count = None
        self._elapsed_ms = None
        self._update_display()

    def set_message(self, message: str) -> None:
        self._message = message
        self._update_display()

    def clear_message(self) -> None:
        self._message = ""
        self._update_display()

    def _update_display(self) -> None:
        parts: list[str] = []

        if self._connection_info:
            parts.append(f"[bold]{self._connection_info}[/bold]")
        elif self._connection_name:
            parts.append(f"[bold]{escape(self._connection_name)}[/bold]")
        else:
            parts.append("[dim]No connection — run: qry <database>[/dim]")

        if self._row_count is not None and self._elapsed_ms is not None:
            parts.append(f"{self._row_count} rows")
            parts.append(f"{self._elapsed_ms:.1f}ms")

        if self._message:
            parts.append(escape(self._message))

        parts.append("[dim]Ctrl+Enter: Run[/dim]")

        self.update(" \u2502 ".join(parts))
