"""Tests for QueryService."""

from pathlib import Path

import pytest

from qry.database.sqlite import SQLiteAdapter
from qry.query.service import QueryService


class TestQueryService:
    """Tests for QueryService."""

    @pytest.fixture
    def query_service(self, sample_sqlite_db: Path) -> QueryService:
        """Create QueryService with SQLite adapter."""
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()
        service = QueryService(adapter=adapter)
        yield service
        adapter.disconnect()

    def test_execute_success(self, query_service: QueryService):
        """Test successful query execution."""
        result = query_service.execute("SELECT * FROM users")

        assert result.is_success
        assert result.row_count == 2

    def test_execute_error(self, query_service: QueryService):
        """Test query execution with error."""
        result = query_service.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert result.error is not None

    def test_execute_adds_to_history(self, query_service: QueryService):
        """Test that successful queries are added to history."""
        query_service.execute("SELECT * FROM users")
        query_service.execute("SELECT 1")

        history = query_service.get_history()

        assert len(history) >= 2

    def test_get_tables(self, query_service: QueryService):
        """Test getting tables through service."""
        tables = query_service.get_tables()

        assert len(tables) == 1
        assert tables[0].name == "users"

    def test_get_completions_for_table(self, query_service: QueryService):
        """Test autocompletion for table names."""
        # "u" at position 1 should suggest "users"
        completions = query_service.get_completions("u", 1)

        table_names = [c.text for c in completions]
        assert "users" in table_names

    def test_search_history(self, query_service: QueryService):
        """Test searching history."""
        query_service.execute("SELECT * FROM users")
        query_service.execute("SELECT id FROM users")

        results = query_service.search_history("users")

        assert len(results) >= 2
