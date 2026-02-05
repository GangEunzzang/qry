"""Query service - business logic layer for query operations."""

from dataclasses import dataclass, field

from qry.database.base import DatabaseAdapter
from qry.query.completion import CompletionItem, CompletionProvider
from qry.query.history import HistoryEntry, HistoryManager
from qry.query.result import QueryResult


@dataclass
class QueryService:
    """Service layer for query operations.

    Integrates query execution, history management, and autocompletion.
    This is the main interface for UI components to interact with query functionality.

    Example:
        >>> service = QueryService(adapter=adapter)
        >>> result = service.execute("SELECT * FROM users")
        >>> history = service.get_history()
    """

    adapter: DatabaseAdapter
    history: HistoryManager = field(default_factory=HistoryManager)
    _completion: CompletionProvider | None = field(default=None, init=False)
    _current_query: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize completion provider."""
        self._completion = CompletionProvider(self.adapter)

    def execute(self, sql: str) -> QueryResult:
        """Execute a SQL query.

        Executes the query and saves to history if successful.

        Args:
            sql: SQL query to execute.

        Returns:
            Query execution result.
        """
        self._current_query = sql
        result = self.adapter.execute(sql)

        if result.is_success:
            self.history.add(sql)

        self._current_query = None
        return result

    def cancel(self) -> None:
        """Cancel the currently running query."""
        self.adapter.cancel()
        self._current_query = None

    @property
    def is_running(self) -> bool:
        """Check if a query is currently running."""
        return self._current_query is not None

    # History methods
    def get_history(self, count: int = 50) -> list[HistoryEntry]:
        """Get recent query history.

        Args:
            count: Number of entries to return.

        Returns:
            List of recent history entries.
        """
        return self.history.get_recent(count)

    def search_history(self, pattern: str) -> list[HistoryEntry]:
        """Search query history.

        Args:
            pattern: Search pattern.

        Returns:
            Matching history entries.
        """
        return self.history.search(pattern)

    def clear_history(self) -> None:
        """Clear all history."""
        self.history.clear()

    def save_history(self) -> None:
        """Save history to disk."""
        self.history.save()

    # Completion methods
    def get_completions(self, text: str, cursor_pos: int) -> list[CompletionItem]:
        """Get autocompletion suggestions.

        Args:
            text: Current SQL text.
            cursor_pos: Cursor position in text.

        Returns:
            List of completion suggestions.
        """
        if self._completion:
            return self._completion.get_completions(text, cursor_pos)
        return []

    def invalidate_schema_cache(self) -> None:
        """Invalidate schema cache for autocompletion."""
        if self._completion:
            self._completion.invalidate_cache()

    # Schema methods (delegated to adapter)
    def get_tables(self):
        """Get list of tables."""
        return self.adapter.get_tables()

    def get_columns(self, table_name: str):
        """Get columns for a table."""
        return self.adapter.get_columns(table_name)
