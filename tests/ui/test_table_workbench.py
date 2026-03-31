"""Tests for Table Workbench screen."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from qry.domains.database.sqlite import SQLiteAdapter
from qry.shared.types import ForeignKeyInfo


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test.db"
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@test.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', NULL)")
    conn.execute(
        "CREATE TABLE orders ("
        "id INTEGER PRIMARY KEY, "
        "user_id INTEGER REFERENCES users(id), "
        "amount REAL)"
    )
    conn.execute("INSERT INTO orders VALUES (1, 1, 99.99)")
    conn.execute("CREATE INDEX idx_orders_user ON orders(user_id)")
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def adapter(db_path: Path) -> SQLiteAdapter:
    a = SQLiteAdapter(db_path)
    a.connect()
    return a


class TestSQLiteGetDDL:
    def test_get_ddl_returns_create_statement(self, adapter: SQLiteAdapter) -> None:
        ddl = adapter.get_ddl("users")
        assert "CREATE TABLE" in ddl
        assert "users" in ddl
        assert "name TEXT" in ddl

    def test_get_ddl_nonexistent_table(self, adapter: SQLiteAdapter) -> None:
        ddl = adapter.get_ddl("nonexistent")
        assert ddl == ""

    def test_get_ddl_not_connected(self, db_path: Path) -> None:
        a = SQLiteAdapter(db_path)
        assert a.get_ddl("users") == ""


class TestSQLiteGetForeignKeys:
    def test_get_foreign_keys(self, adapter: SQLiteAdapter) -> None:
        # Enable FK support for this connection
        adapter._conn.execute("PRAGMA foreign_keys = ON")
        fks = adapter.get_foreign_keys("orders")
        assert len(fks) == 1
        assert fks[0].from_column == "user_id"
        assert fks[0].to_table == "users"
        assert fks[0].to_column == "id"

    def test_no_foreign_keys(self, adapter: SQLiteAdapter) -> None:
        fks = adapter.get_foreign_keys("users")
        assert fks == []

    def test_not_connected(self, db_path: Path) -> None:
        a = SQLiteAdapter(db_path)
        assert a.get_foreign_keys("orders") == []


class TestTableWorkbenchScreen:
    """Basic structural tests for the workbench screen."""

    def test_workbench_creates_with_table_name(self, adapter: SQLiteAdapter) -> None:
        from qry.ui.screens.screen_table_workbench import TableWorkbench
        wb = TableWorkbench("users", adapter)
        assert wb._table_name == "users"

    def test_workbench_has_escape_binding(self) -> None:
        from qry.ui.screens.screen_table_workbench import TableWorkbench
        keys = [b.key for b in TableWorkbench.BINDINGS]
        assert "escape" in keys
