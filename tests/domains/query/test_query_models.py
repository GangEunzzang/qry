"""Tests for query models."""

from datetime import datetime

from qry.domains.query.models import CompletionItem, HistoryEntry, QueryResult


class TestQueryResult:
    def test_success_result(self):
        result = QueryResult(
            columns=["id", "name"],
            rows=[(1, "Alice"), (2, "Bob")],
            row_count=2,
            execution_time_ms=5.0,
        )

        assert result.is_success
        assert not result.is_empty
        assert result.row_count == 2
        assert result.error is None

    def test_error_result(self):
        result = QueryResult(error="Table not found")

        assert not result.is_success
        assert result.error == "Table not found"

    def test_error_with_position(self):
        result = QueryResult(error="Syntax error", error_position=10)

        assert not result.is_success
        assert result.error_position == 10

    def test_empty_result(self):
        result = QueryResult(
            columns=["id"],
            rows=[],
            row_count=0,
            execution_time_ms=1.0,
        )

        assert result.is_success
        assert result.is_empty

    def test_default_values(self):
        result = QueryResult()

        assert result.columns == []
        assert result.rows == []
        assert result.row_count == 0
        assert result.execution_time_ms == 0.0
        assert result.error is None


class TestHistoryEntry:
    def test_creation(self):
        now = datetime.now()
        entry = HistoryEntry(
            query="SELECT * FROM users",
            timestamp=now,
            connection_name="test_db",
        )

        assert entry.query == "SELECT * FROM users"
        assert entry.timestamp == now
        assert entry.connection_name == "test_db"

    def test_optional_connection_name(self):
        entry = HistoryEntry(
            query="SELECT 1",
            timestamp=datetime.now(),
        )

        assert entry.connection_name is None


class TestCompletionItem:
    def test_table_completion(self):
        item = CompletionItem(
            text="users",
            kind="table",
            detail="Table (100 rows)",
        )

        assert item.text == "users"
        assert item.kind == "table"
        assert item.detail == "Table (100 rows)"

    def test_column_completion(self):
        item = CompletionItem(
            text="email",
            kind="column",
            detail="TEXT",
        )

        assert item.text == "email"
        assert item.kind == "column"
        assert item.detail == "TEXT"

    def test_optional_detail(self):
        item = CompletionItem(text="SELECT", kind="keyword")

        assert item.detail is None
