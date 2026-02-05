"""Query executor service."""

from qry.database.base import DatabaseAdapter
from qry.query.history import HistoryManager
from qry.query.result import QueryResult


class QueryExecutor:
    """Executes queries and manages query lifecycle."""

    def __init__(
        self,
        adapter: DatabaseAdapter,
        history: HistoryManager | None = None,
    ) -> None:
        """Initialize query executor.

        Args:
            adapter: Database adapter for query execution.
            history: Optional history manager for saving queries.
        """
        self._adapter = adapter
        self._history = history
        self._current_query: str | None = None

    def execute(self, sql: str) -> QueryResult:
        """Execute a SQL query.

        Args:
            sql: SQL query to execute.

        Returns:
            Query execution result.
        """
        self._current_query = sql
        result = self._adapter.execute(sql)

        if self._history and result.is_success:
            self._history.add(sql)

        self._current_query = None
        return result

    def cancel(self) -> None:
        """Cancel the currently running query."""
        self._adapter.cancel()
        self._current_query = None

    @property
    def is_running(self) -> bool:
        """Check if a query is currently running."""
        return self._current_query is not None
