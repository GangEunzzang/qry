"""Query history management."""

from dataclasses import dataclass, field
from datetime import datetime

from qry.domains.query.models import HistoryEntry
from qry.domains.query.repository import HistoryRepository
from qry.infrastructure.repositories.json_history import JsonHistoryRepository


@dataclass
class HistoryManager:
    """Manages query history with persistence.

    Uses repository pattern for storage, allowing different
    backends (JSON, database, etc.)
    """

    max_entries: int = 1000
    _repository: HistoryRepository = field(default_factory=JsonHistoryRepository)
    _entries: list[HistoryEntry] = field(default_factory=list)
    _connection_name: str | None = None

    def __post_init__(self) -> None:
        self._load()

    def _load(self) -> None:
        self._entries = self._repository.load()

    def save(self) -> None:
        self._repository.save(self._entries)

    def add(self, query: str) -> None:
        entry = HistoryEntry(
            query=query.strip(),
            timestamp=datetime.now(),
            connection_name=self._connection_name,
        )
        self._entries.append(entry)

        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def search(self, pattern: str) -> list[HistoryEntry]:
        pattern_lower = pattern.lower()
        return [e for e in self._entries if pattern_lower in e.query.lower()]

    def get_recent(self, count: int = 50) -> list[HistoryEntry]:
        return list(reversed(self._entries[-count:]))

    def clear(self) -> None:
        self._entries = []

    def set_connection(self, connection_name: str) -> None:
        self._connection_name = connection_name
