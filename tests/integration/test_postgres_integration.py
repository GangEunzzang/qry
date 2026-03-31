"""PostgreSQL integration tests — require Docker container."""

import pytest


@pytest.mark.integration
class TestPostgresIntegration:
    def test_is_connected(self, postgres_adapter):
        assert postgres_adapter.is_connected()

    def test_execute_select(self, postgres_adapter):
        result = postgres_adapter.execute("SELECT 1 AS num")
        assert result.is_success
        assert result.columns == ["num"]
        assert result.rows[0][0] == 1

    def test_get_tables(self, postgres_adapter):
        tables = postgres_adapter.get_tables()
        names = [t.name for t in tables]
        assert "test_users" in names

    def test_get_columns(self, postgres_adapter):
        columns = postgres_adapter.get_columns("test_users")
        names = [c.name for c in columns]
        assert "id" in names
        assert "name" in names
        assert "email" in names

    def test_execute_error(self, postgres_adapter):
        result = postgres_adapter.execute("SELECT * FROM nonexistent_table_xyz")
        assert result.error is not None

    def test_get_views(self, postgres_adapter):
        views = postgres_adapter.get_views()
        assert isinstance(views, list)

    def test_get_indexes(self, postgres_adapter):
        indexes = postgres_adapter.get_indexes()
        assert isinstance(indexes, list)
