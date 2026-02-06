"""Tests for PostgreSQL adapter (mock-based, no real DB required)."""

from unittest.mock import MagicMock, patch

import pytest

from qry.shared.exceptions import DatabaseError
from qry.shared.types import ColumnInfo, TableInfo


@pytest.fixture
def mock_connection():
    conn = MagicMock()
    conn.closed = False
    return conn


@pytest.fixture
def adapter():
    from qry.domains.database.postgres import PostgresAdapter

    return PostgresAdapter(
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
    )


class TestPostgresConnect:

    @patch("qry.domains.database.postgres.psycopg")
    def test_connect_success(self, mock_psycopg, adapter):
        mock_conn = MagicMock()
        mock_conn.closed = False
        mock_psycopg.connect.return_value = mock_conn

        adapter.connect()

        assert adapter.is_connected()
        mock_psycopg.connect.assert_called_once_with(
            host="localhost",
            port=5432,
            dbname="testdb",
            user="testuser",
            password="testpass",
            autocommit=True,
        )

    @patch("qry.domains.database.postgres.psycopg")
    def test_connect_failure(self, mock_psycopg, adapter):
        import psycopg

        mock_psycopg.Error = psycopg.Error
        mock_psycopg.connect.side_effect = psycopg.Error("connection refused")

        with pytest.raises(DatabaseError, match="Failed to connect"):
            adapter.connect()

        assert not adapter.is_connected()


class TestPostgresDisconnect:

    @patch("qry.domains.database.postgres.psycopg")
    def test_disconnect(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection
        adapter.connect()

        adapter.disconnect()

        assert not adapter.is_connected()
        mock_connection.close.assert_called_once()

    def test_disconnect_when_not_connected(self, adapter):
        adapter.disconnect()
        assert not adapter.is_connected()


class TestPostgresExecute:

    @patch("qry.domains.database.postgres.psycopg")
    def test_execute_select(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.fetchall.return_value = [
            (1, "Alice", "alice@example.com"),
            (2, "Bob", "bob@example.com"),
        ]
        mock_connection.execute.return_value = mock_cursor

        adapter.connect()
        result = adapter.execute("SELECT * FROM users")

        assert result.is_success
        assert result.columns == ["id", "name", "email"]
        assert result.row_count == 2
        assert len(result.rows) == 2
        assert result.execution_time_ms > 0

    @patch("qry.domains.database.postgres.psycopg")
    def test_execute_insert(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 1
        mock_connection.execute.return_value = mock_cursor

        adapter.connect()
        result = adapter.execute("INSERT INTO users VALUES (3, 'Charlie', 'c@test.com')")

        assert result.is_success
        assert result.columns == []
        assert result.row_count == 1

    @patch("qry.domains.database.postgres.psycopg")
    def test_execute_error(self, mock_psycopg, adapter, mock_connection):
        import psycopg

        mock_psycopg.connect.return_value = mock_connection
        mock_psycopg.Error = psycopg.Error
        mock_connection.execute.side_effect = psycopg.Error("relation does not exist")

        adapter.connect()
        result = adapter.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert "relation does not exist" in result.error
        assert result.execution_time_ms > 0

    def test_execute_not_connected(self, adapter):
        result = adapter.execute("SELECT 1")

        assert not result.is_success
        assert result.error == "Not connected to database"


class TestPostgresGetTables:

    @patch("qry.domains.database.postgres.psycopg")
    def test_get_tables(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("users",), ("orders",)]
        mock_connection.execute.return_value = mock_cursor

        adapter.connect()
        tables = adapter.get_tables()

        assert len(tables) == 2
        assert tables[0] == TableInfo(name="users", schema="public")
        assert tables[1] == TableInfo(name="orders", schema="public")

    def test_get_tables_not_connected(self, adapter):
        tables = adapter.get_tables()
        assert tables == []


class TestPostgresGetColumns:

    @patch("qry.domains.database.postgres.psycopg")
    def test_get_columns(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        col_cursor = MagicMock()
        col_cursor.fetchall.return_value = [
            ("id", "integer", "NO", None),
            ("name", "character varying", "YES", None),
            ("email", "character varying", "YES", "'unknown'"),
        ]

        pk_cursor = MagicMock()
        pk_cursor.fetchall.return_value = [("id",)]

        mock_connection.execute.side_effect = [col_cursor, pk_cursor]

        adapter.connect()
        columns = adapter.get_columns("users")

        assert len(columns) == 3
        assert columns[0] == ColumnInfo(
            name="id", data_type="integer", nullable=False, primary_key=True, default=None
        )
        assert columns[1] == ColumnInfo(
            name="name", data_type="character varying", nullable=True, primary_key=False
        )
        assert columns[2] == ColumnInfo(
            name="email",
            data_type="character varying",
            nullable=True,
            primary_key=False,
            default="'unknown'",
        )

    def test_get_columns_not_connected(self, adapter):
        columns = adapter.get_columns("users")
        assert columns == []


class TestPostgresGetDatabases:

    @patch("qry.domains.database.postgres.psycopg")
    def test_get_databases(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("postgres",), ("testdb",)]
        mock_connection.execute.return_value = mock_cursor

        adapter.connect()
        databases = adapter.get_databases()

        assert databases == ["postgres", "testdb"]

    def test_get_databases_not_connected(self, adapter):
        databases = adapter.get_databases()
        assert databases == []


class TestPostgresCancel:

    @patch("qry.domains.database.postgres.psycopg")
    def test_cancel(self, mock_psycopg, adapter, mock_connection):
        mock_psycopg.connect.return_value = mock_connection

        adapter.connect()
        adapter.cancel()

        mock_connection.cancel.assert_called_once()

    def test_cancel_not_connected(self, adapter):
        adapter.cancel()
