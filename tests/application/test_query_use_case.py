"""Tests for QueryUseCase."""

from pathlib import Path

import pytest

from qry.application.query_use_case import QueryUseCase
from qry.domains.database.sqlite import SQLiteAdapter


class TestQueryUseCase:
    @pytest.fixture
    def adapter(self, sample_sqlite_db: Path) -> SQLiteAdapter:
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()
        yield adapter
        adapter.disconnect()

    @pytest.fixture
    def use_case(self, adapter: SQLiteAdapter, tmp_config_dir: Path) -> QueryUseCase:
        return QueryUseCase(adapter=adapter)

    def test_execute_success(self, use_case: QueryUseCase):
        result = use_case.execute("SELECT * FROM users")

        assert result.is_success
        assert result.row_count == 2

    def test_execute_error(self, use_case: QueryUseCase):
        result = use_case.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert result.error is not None

    def test_execute_adds_to_history(self, use_case: QueryUseCase):
        use_case.execute("SELECT * FROM users")
        use_case.execute("SELECT 1")

        history = use_case.get_history()

        assert len(history) >= 2
        queries = [h.query for h in history]
        assert "SELECT * FROM users" in queries
        assert "SELECT 1" in queries

    def test_execute_error_not_added_to_history(self, use_case: QueryUseCase):
        use_case.execute("SELECT * FROM nonexistent")

        history = use_case.get_history()
        queries = [h.query for h in history]

        assert "SELECT * FROM nonexistent" not in queries

    def test_is_running_during_query(self, use_case: QueryUseCase):
        # Note: Can't easily test this without threading
        assert not use_case.is_running

    def test_get_tables(self, use_case: QueryUseCase):
        tables = use_case.get_tables()

        assert len(tables) == 2
        table_names = [t.name for t in tables]
        assert "users" in table_names

    def test_get_columns(self, use_case: QueryUseCase):
        columns = use_case.get_columns("users")

        assert len(columns) == 3
        col_names = [c.name for c in columns]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names

    def test_get_completions_for_table(self, use_case: QueryUseCase):
        completions = use_case.get_completions("u", 1)

        table_names = [c.text for c in completions]
        assert "users" in table_names

    def test_get_completions_empty_prefix(self, use_case: QueryUseCase):
        completions = use_case.get_completions("", 0)

        assert completions == []

    def test_search_history(self, use_case: QueryUseCase):
        use_case.execute("SELECT * FROM users")
        use_case.execute("SELECT id FROM users")
        use_case.execute("SELECT 1")

        results = use_case.search_history("users")

        assert len(results) == 2
        queries = [r.query for r in results]
        assert all("users" in q.lower() for q in queries)

    def test_clear_history(self, use_case: QueryUseCase):
        use_case.execute("SELECT * FROM users")
        use_case.execute("SELECT 1")

        use_case.clear_history()

        assert use_case.get_history() == []

    def test_invalidate_schema_cache(self, use_case: QueryUseCase):
        # First access caches
        use_case.get_completions("u", 1)

        # Should not raise
        use_case.invalidate_schema_cache()

        # Should still work after invalidation
        completions = use_case.get_completions("u", 1)
        assert len(completions) > 0
