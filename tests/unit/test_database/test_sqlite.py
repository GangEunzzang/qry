"""Tests for SQLite adapter."""

from pathlib import Path

import pytest

from qry.database.database_sqlite import SQLiteAdapter


class TestSQLiteAdapter:

    def test_connect_success(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()
        assert adapter.is_connected()
        adapter.disconnect()

    def test_disconnect(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()
        adapter.disconnect()
        assert not adapter.is_connected()

    def test_execute_select(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT * FROM users")

        assert result.is_success
        assert result.columns == ["id", "name", "email"]
        assert result.row_count == 2
        assert len(result.rows) == 2

        adapter.disconnect()

    def test_execute_invalid_query(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert result.error is not None
        assert "nonexistent" in result.error.lower()

        adapter.disconnect()

    def test_get_tables(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        tables = adapter.get_tables()

        assert len(tables) == 1
        assert tables[0].name == "users"

        adapter.disconnect()

    def test_get_columns(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        columns = adapter.get_columns("users")

        assert len(columns) == 3
        column_names = [c.name for c in columns]
        assert "id" in column_names
        assert "name" in column_names
        assert "email" in column_names

        adapter.disconnect()
