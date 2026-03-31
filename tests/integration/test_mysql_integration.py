"""MySQL integration tests — require Docker container."""

import pytest


@pytest.mark.integration
class TestMySQLIntegration:
    def test_is_connected(self, mysql_adapter):
        assert mysql_adapter.is_connected()

    def test_execute_select(self, mysql_adapter):
        result = mysql_adapter.execute("SELECT 1 AS num")
        assert result.is_success
        assert result.columns == ["num"]

    def test_get_tables(self, mysql_adapter):
        tables = mysql_adapter.get_tables()
        names = [t.name for t in tables]
        assert "test_users" in names

    def test_get_columns(self, mysql_adapter):
        columns = mysql_adapter.get_columns("test_users")
        names = [c.name for c in columns]
        assert "id" in names
        assert "name" in names

    def test_execute_error(self, mysql_adapter):
        result = mysql_adapter.execute("SELECT * FROM nonexistent_table_xyz")
        assert result.error is not None

    def test_get_databases(self, mysql_adapter):
        dbs = mysql_adapter.get_databases()
        assert isinstance(dbs, list)
        assert len(dbs) > 0
