"""Query history repository abstraction."""

from abc import ABC, abstractmethod

from qry.domains.query.models import HistoryEntry


class HistoryRepository(ABC):
    """Abstract repository for query history.

    Implementations handle the actual persistence mechanism
    (JSON files, database, etc.)
    """

    @abstractmethod
    def load(self) -> list[HistoryEntry]:
        """Load all history entries."""
        pass

    @abstractmethod
    def save(self, entries: list[HistoryEntry]) -> None:
        """Save all history entries."""
        pass
