"""JSON-based history repository implementation."""

import json
from datetime import datetime
from pathlib import Path

from qry.domains.query.models import HistoryEntry
from qry.domains.query.repository import HistoryRepository
from qry.shared.paths import get_data_dir


class JsonHistoryRepository(HistoryRepository):
    """Persists query history to JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (get_data_dir() / "history.json")

    def load(self) -> list[HistoryEntry]:
        if not self._path.exists():
            return []

        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            return [
                HistoryEntry(
                    query=entry["query"],
                    timestamp=datetime.fromisoformat(entry["timestamp"]),
                    connection_name=entry.get("connection_name"),
                )
                for entry in data.get("entries", [])
            ]
        except (OSError, json.JSONDecodeError, KeyError):
            return []

    def save(self, entries: list[HistoryEntry]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "entries": [
                {
                    "query": entry.query,
                    "timestamp": entry.timestamp.isoformat(),
                    "connection_name": entry.connection_name,
                }
                for entry in entries
            ]
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
