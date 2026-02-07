"""Query use case - application layer orchestration."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qry.domains.query.completion import CompletionProvider
from qry.domains.query.history import HistoryManager
from qry.domains.query.models import CompletionItem, HistoryEntry
from qry.domains.query.splitter import QuerySplitter
from qry.shared.models import QueryResult
from qry.shared.types import ColumnInfo, TableInfo

if TYPE_CHECKING:
    from qry.domains.database.base import DatabaseAdapter


@dataclass
class QueryUseCase:
    """Application service - orchestrates query execution, history, and completion."""

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

    def execute_multi(self, sql: str) -> list[QueryResult]:
        """Execute multiple semicolon-separated statements."""
        statements = QuerySplitter.split(sql)
        if not statements:
            return [QueryResult(error="No statements to execute")]

        if len(statements) == 1:
            return [self.execute(statements[0])]

        results: list[QueryResult] = []
        for stmt in statements:
            result = self.execute(stmt)
            results.append(result)
            if not result.is_success:
                break
        return results

    def cancel(self) -> None:
        self.adapter.cancel()
        self._current_query = None

    @property
    def is_running(self) -> bool:
        return self._current_query is not None

    def get_history(self, count: int = 50) -> list[HistoryEntry]:
        return self.history.get_recent(count)

    def search_history(self, pattern: str, limit: int = 50) -> list[HistoryEntry]:
        return self.history.search_reverse(pattern, limit=limit)

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

    def get_tables(self) -> list[TableInfo]:
        return self.adapter.get_tables()

    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        return self.adapter.get_columns(table_name)
