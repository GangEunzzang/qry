"""Tests for SQLite adapter."""

from pathlib import Path

import pytest

from qry.domains.database.sqlite import SQLiteAdapter
from qry.shared.exceptions import DatabaseError


class TestSQLiteAdapter:
    def test_connect_success(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)

        adapter.connect()

        assert adapter.is_connected()
        adapter.disconnect()

    def test_connect_creates_new_db(self, tmp_path: Path):
        db_path = tmp_path / "new.db"
        adapter = SQLiteAdapter(db_path)

        adapter.connect()

        assert adapter.is_connected()
        assert db_path.exists()
        adapter.disconnect()

    def test_disconnect(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        adapter.disconnect()

        assert not adapter.is_connected()

    def test_disconnect_when_not_connected(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)

        adapter.disconnect()  # Should not raise

    def test_execute_select(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT * FROM users ORDER BY id")

        assert result.is_success
        assert result.columns == ["id", "name", "email"]
        assert result.row_count == 2
        assert len(result.rows) == 2
        assert result.rows[0] == (1, "Alice", "alice@example.com")

        adapter.disconnect()

    def test_execute_select_with_where(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT name FROM users WHERE id = 1")

        assert result.is_success
        assert result.row_count == 1
        assert result.rows[0] == ("Alice",)

        adapter.disconnect()

    def test_execute_insert(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("INSERT INTO users VALUES (3, 'Charlie', 'charlie@example.com')")

        assert result.is_success
        assert result.row_count == 1

        adapter.disconnect()

    def test_execute_invalid_query(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert result.error is not None
        assert "nonexistent" in result.error.lower()

        adapter.disconnect()

    def test_execute_syntax_error(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELEC * FROM users")

        assert not result.is_success
        assert result.error is not None

        adapter.disconnect()

    def test_execute_when_not_connected(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)

        result = adapter.execute("SELECT 1")

        assert not result.is_success
        assert "not connected" in result.error.lower()

    def test_execution_time_recorded(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        result = adapter.execute("SELECT * FROM users")

        assert result.execution_time_ms >= 0

        adapter.disconnect()

    def test_get_tables(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        tables = adapter.get_tables()

        assert len(tables) == 2
        table_names = [t.name for t in tables]
        assert "users" in table_names
        assert "posts" in table_names

        adapter.disconnect()

    def test_get_tables_empty_db(self, empty_sqlite_db: Path):
        adapter = SQLiteAdapter(empty_sqlite_db)
        adapter.connect()

        tables = adapter.get_tables()

        assert tables == []

        adapter.disconnect()

    def test_get_columns(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        columns = adapter.get_columns("users")

        assert len(columns) == 3
        col_names = [c.name for c in columns]
        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names

        id_col = next(c for c in columns if c.name == "id")
        assert id_col.primary_key is True
        assert id_col.data_type == "INTEGER"

        adapter.disconnect()

    def test_get_columns_with_special_chars(self, tmp_path: Path):
        db_path = tmp_path / "special.db"
        import sqlite3

        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE "table with spaces" (id INTEGER)')
        conn.close()

        adapter = SQLiteAdapter(db_path)
        adapter.connect()

        columns = adapter.get_columns("table with spaces")

        assert len(columns) == 1
        assert columns[0].name == "id"

        adapter.disconnect()

    def test_get_databases(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        databases = adapter.get_databases()

        assert "main" in databases

        adapter.disconnect()

    def test_cancel(self, sample_sqlite_db: Path):
        adapter = SQLiteAdapter(sample_sqlite_db)
        adapter.connect()

        adapter.cancel()  # Should not raise

        adapter.disconnect()
