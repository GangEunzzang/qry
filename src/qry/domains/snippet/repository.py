"""Snippet repository abstraction."""

from abc import ABC, abstractmethod

from qry.domains.snippet.models import Snippet


class SnippetRepository(ABC):
    """Abstract repository for SQL snippets."""

    @abstractmethod
    def list_all(self) -> list[Snippet]:
        """Load all snippets."""

    @abstractmethod
    def get(self, name: str) -> Snippet | None:
        """Get a snippet by name."""

    @abstractmethod
    def save(self, snippet: Snippet) -> None:
        """Save a snippet (create or update)."""

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Delete a snippet by name. Returns True if deleted."""
