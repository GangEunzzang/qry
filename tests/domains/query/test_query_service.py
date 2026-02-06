"""Tests for QueryService."""

from pathlib import Path

import pytest

from qry.domains.database.sqlite import SQLiteAdapter
from qry.domains.query.service import QueryService


class TestQueryService:
    @pytest.fixture
    def adapter(self, sample_sqlite_db: Path) -> SQLiteAdapter:
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()
        yield adapter
        adapter.disconnect()

    @pytest.fixture
    def service(self, adapter: SQLiteAdapter, tmp_config_dir: Path) -> QueryService:
        return QueryService(adapter=adapter)

    def test_execute_success(self, service: QueryService):
        result = service.execute("SELECT * FROM users")

        assert result.is_success
        assert result.row_count == 2

    def test_execute_error(self, service: QueryService):
        result = service.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert result.error is not None

    def test_execute_adds_to_history(self, service: QueryService):
        service.execute("SELECT * FROM users")
        service.execute("SELECT 1")

        history = service.get_history()

        assert len(history) >= 2
        queries = [h.query for h in history]
        assert "SELECT * FROM users" in queries
        assert "SELECT 1" in queries

    def test_execute_error_not_added_to_history(self, service: QueryService):
        service.execute("SELECT * FROM nonexistent")

        history = service.get_history()
        queries = [h.query for h in history]

        assert "SELECT * FROM nonexistent" not in queries

    def test_is_running_during_query(self, service: QueryService):
        # Note: Can't easily test this without threading
        assert not service.is_running

    def test_get_tables(self, service: QueryService):
        tables = service.get_tables()

        assert len(tables) == 2
        table_names = [t.name for t in tables]
        assert "users" in table_names

    def test_get_columns(self, service: QueryService):
        columns = service.get_columns("users")

        assert len(columns) == 3
        col_names = [c.name for c in columns]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names

    def test_get_completions_for_table(self, service: QueryService):
        completions = service.get_completions("u", 1)

        table_names = [c.text for c in completions]
        assert "users" in table_names

    def test_get_completions_empty_prefix(self, service: QueryService):
        completions = service.get_completions("", 0)

        assert completions == []

    def test_search_history(self, service: QueryService):
        service.execute("SELECT * FROM users")
        service.execute("SELECT id FROM users")
        service.execute("SELECT 1")

        results = service.search_history("users")

        assert len(results) == 2
        queries = [r.query for r in results]
        assert all("users" in q.lower() for q in queries)

    def test_clear_history(self, service: QueryService):
        service.execute("SELECT * FROM users")
        service.execute("SELECT 1")

        service.clear_history()

        assert service.get_history() == []

    def test_invalidate_schema_cache(self, service: QueryService):
        # First access caches
        service.get_completions("u", 1)

        # Should not raise
        service.invalidate_schema_cache()

        # Should still work after invalidation
        completions = service.get_completions("u", 1)
        assert len(completions) > 0
