"""Query history management."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from qry.settings.paths import get_data_dir


@dataclass
class HistoryEntry:
    """A single history entry."""

    query: str
    timestamp: datetime
    connection_name: str | None = None


@dataclass
class HistoryManager:
    """Manages query history."""

    max_entries: int = 1000
    _entries: list[HistoryEntry] = field(default_factory=list)
    _connection_name: str | None = None

    def __post_init__(self) -> None:
        """Load history after initialization."""
        self._load()

    def _get_history_path(self) -> Path:
        """Get history file path."""
        return get_data_dir() / "history.json"

    def _load(self) -> None:
        """Load history from file."""
        path = self._get_history_path()
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = json.load(f)
            self._entries = [
                HistoryEntry(
                    query=entry["query"],
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    connection_name=entry.get("connection_name"),
                )
                for entry in data.get("entries", [])
            ]
        except (json.JSONDecodeError, KeyError):
            self._entries = []

    def save(self) -> None:
        """Save history to file."""
        path = self._get_history_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "entries": [
                {
                    "query": entry.query,
                    "timestamp": entry.timestamp.isoformat(),
                    "connection_name": entry.connection_name,
                }
                for entry in self._entries
            ]
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, query: str) -> None:
        """Add a query to history.

        Args:
            query: Query string to add.
        """
        entry = HistoryEntry(
            query=query.strip(),
            timestamp=datetime.now(),
            connection_name=self._connection_name,
        )
        self._entries.append(entry)

        # Trim to max entries
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def search(self, pattern: str) -> list[HistoryEntry]:
        """Search history for matching queries.

        Args:
            pattern: Search pattern (case-insensitive substring match).

        Returns:
            List of matching history entries.
        """
        pattern_lower = pattern.lower()
        return [e for e in self._entries if pattern_lower in e.query.lower()]

    def get_recent(self, count: int = 50) -> list[HistoryEntry]:
        """Get recent history entries.

        Args:
            count: Number of entries to return.

        Returns:
            List of recent history entries (newest first).
        """
        return list(reversed(self._entries[-count:]))

    def clear(self) -> None:
        """Clear all history."""
        self._entries = []

    def set_connection(self, connection_name: str) -> None:
        """Set current connection name for new entries.

        Args:
            connection_name: Connection name to associate with new entries.
        """
        self._connection_name = connection_name
