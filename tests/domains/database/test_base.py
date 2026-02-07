"""Tests for DatabaseAdapter.test_connection()."""

from qry.domains.database.base import DatabaseAdapter
from qry.shared.models import QueryResult


class ConcreteAdapter(DatabaseAdapter):
    """Concrete adapter for testing the base class."""

    def __init__(self) -> None:
        self._connected = False
        self._execute_result: QueryResult | None = None

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def execute(self, sql: str) -> QueryResult:
        if self._execute_result is not None:
            return self._execute_result
        return QueryResult(columns=["1"], rows=[(1,)], row_count=1)

    def get_tables(self) -> list:
        return []

    def get_columns(self, table_name: str) -> list:
        return []

    def get_databases(self) -> list[str]:
        return []


class TestTestConnection:
    def test_success_when_connected(self):
        adapter = ConcreteAdapter()
        adapter.connect()

        success, message = adapter.test_connection()

        assert success is True
        assert message == "Connection successful"
        assert adapter.is_connected()  # should remain connected

    def test_success_when_not_connected(self):
        adapter = ConcreteAdapter()

        success, message = adapter.test_connection()

        assert success is True
        assert message == "Connection successful"
        assert not adapter.is_connected()  # should disconnect after test

    def test_failure_when_execute_returns_error(self):
        adapter = ConcreteAdapter()
        adapter.connect()
        adapter._execute_result = QueryResult(error="table not found")

        success, message = adapter.test_connection()

        assert success is False
        assert message == "table not found"
        assert adapter.is_connected()  # should remain connected

    def test_failure_when_connect_raises(self):
        adapter = ConcreteAdapter()

        def failing_connect() -> None:
            raise ConnectionError("connection refused")
        adapter.connect = failing_connect

        success, message = adapter.test_connection()

        assert success is False
        assert "connection refused" in message

    def test_stays_connected_when_already_connected(self):
        adapter = ConcreteAdapter()
        adapter.connect()
        assert adapter.is_connected()

        adapter.test_connection()

        assert adapter.is_connected()

    def test_disconnects_when_was_not_connected(self):
        adapter = ConcreteAdapter()
        assert not adapter.is_connected()

        adapter.test_connection()

        assert not adapter.is_connected()
