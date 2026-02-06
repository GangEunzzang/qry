"""Query service - business logic layer for query operations."""

from dataclasses import dataclass, field

from qry.domains.query.completion import CompletionProvider
from qry.domains.query.history import HistoryManager
from qry.domains.query.models import CompletionItem, HistoryEntry, QueryResult

# Use TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qry.domains.database.base import DatabaseAdapter


@dataclass
class QueryService:
    """Service layer for query operations."""

    adapter: "DatabaseAdapter"
    history: HistoryManager = field(default_factory=HistoryManager)
    _completion: CompletionProvider | None = field(default=None, init=False)
    _current_query: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._completion = CompletionProvider(self.adapter)

    def execute(self, sql: str) -> QueryResult:
        self._current_query = sql
        try:
            result = self.adapter.execute(sql)
            if result.is_success:
                self.history.add(sql)
            return result
        finally:
            self._current_query = None

    def cancel(self) -> None:
        self.adapter.cancel()
        self._current_query = None

    @property
    def is_running(self) -> bool:
        return self._current_query is not None

    def get_history(self, count: int = 50) -> list[HistoryEntry]:
        return self.history.get_recent(count)

    def search_history(self, pattern: str) -> list[HistoryEntry]:
        return self.history.search(pattern)

    def clear_history(self) -> None:
        self.history.clear()

    def save_history(self) -> None:
        self.history.save()

    def get_completions(self, text: str, cursor_pos: int) -> list[CompletionItem]:
        if self._completion:
            return self._completion.get_completions(text, cursor_pos)
        return []

    def invalidate_schema_cache(self) -> None:
        if self._completion:
            self._completion.invalidate_cache()

    def get_tables(self):
        return self.adapter.get_tables()

    def get_columns(self, table_name: str):
        return self.adapter.get_columns(table_name)
