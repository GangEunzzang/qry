"""Query executor service."""

from qry.database.database_base import DatabaseAdapter
from qry.query.query_history import HistoryManager
from qry.query.query_result import QueryResult


class QueryExecutor:
    """Executes queries and manages query lifecycle."""

    def __init__(
        self,
        adapter: DatabaseAdapter,
        history: HistoryManager | None = None,
    ) -> None:
        self._adapter = adapter
        self._history = history
        self._current_query: str | None = None

    def execute(self, sql: str) -> QueryResult:
        self._current_query = sql
        result = self._adapter.execute(sql)

        if self._history and result.is_success:
            self._history.add(sql)

        self._current_query = None
        return result

    def cancel(self) -> None:
        self._adapter.cancel()
        self._current_query = None

    @property
    def is_running(self) -> bool:
        return self._current_query is not None
