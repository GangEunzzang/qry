"""Tests for MySQL adapter (mock-based, no real DB required)."""

from unittest.mock import MagicMock, patch

import pytest

from qry.shared.exceptions import DatabaseError
from qry.shared.types import ColumnInfo, TableInfo


@pytest.fixture
def mock_connection():
    conn = MagicMock()
    conn.open = True
    return conn


@pytest.fixture
def adapter():
    from qry.domains.database.mysql import MySQLAdapter

    return MySQLAdapter(
        host="localhost",
        port=3306,
        database="testdb",
        user="testuser",
        password="testpass",
    )


class TestMySQLConnect:

    @patch("qry.domains.database.mysql.pymysql")
    def test_connect_success(self, mock_pymysql, adapter):
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_pymysql.connect.return_value = mock_conn

        adapter.connect()

        assert adapter.is_connected()
        mock_pymysql.connect.assert_called_once_with(
            host="localhost",
            port=3306,
            database="testdb",
            user="testuser",
            password="testpass",
            autocommit=True,
        )

    @patch("qry.domains.database.mysql.pymysql")
    def test_connect_failure(self, mock_pymysql, adapter):
        import pymysql

        mock_pymysql.Error = pymysql.Error
        mock_pymysql.connect.side_effect = pymysql.Error("connection refused")

        with pytest.raises(DatabaseError, match="Failed to connect"):
            adapter.connect()

        assert not adapter.is_connected()


class TestMySQLDisconnect:

    @patch("qry.domains.database.mysql.pymysql")
    def test_disconnect(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection
        adapter.connect()

        adapter.disconnect()

        assert not adapter.is_connected()
        mock_connection.close.assert_called_once()

    def test_disconnect_when_not_connected(self, adapter):
        adapter.disconnect()
        assert not adapter.is_connected()


class TestMySQLExecute:

    @patch("qry.domains.database.mysql.pymysql")
    def test_execute_select(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",), ("email",)]
        mock_cursor.fetchall.return_value = [
            (1, "Alice", "alice@example.com"),
            (2, "Bob", "bob@example.com"),
        ]
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        result = adapter.execute("SELECT * FROM users")

        assert result.is_success
        assert result.columns == ["id", "name", "email"]
        assert result.row_count == 2
        assert len(result.rows) == 2
        assert result.execution_time_ms > 0

    @patch("qry.domains.database.mysql.pymysql")
    def test_execute_insert(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        result = adapter.execute("INSERT INTO users VALUES (3, 'Charlie', 'c@test.com')")

        assert result.is_success
        assert result.columns == []
        assert result.row_count == 1

    @patch("qry.domains.database.mysql.pymysql")
    def test_execute_error(self, mock_pymysql, adapter, mock_connection):
        import pymysql

        mock_pymysql.connect.return_value = mock_connection
        mock_pymysql.Error = pymysql.Error

        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = pymysql.Error("table does not exist")
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        result = adapter.execute("SELECT * FROM nonexistent")

        assert not result.is_success
        assert "table does not exist" in result.error
        assert result.execution_time_ms > 0

    def test_execute_not_connected(self, adapter):
        result = adapter.execute("SELECT 1")

        assert not result.is_success
        assert result.error == "Not connected to database"


class TestMySQLGetTables:

    @patch("qry.domains.database.mysql.pymysql")
    def test_get_tables(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("users",), ("orders",)]
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        tables = adapter.get_tables()

        assert len(tables) == 2
        assert tables[0] == TableInfo(name="users")
        assert tables[1] == TableInfo(name="orders")

    def test_get_tables_not_connected(self, adapter):
        tables = adapter.get_tables()
        assert tables == []


class TestMySQLGetColumns:

    @patch("qry.domains.database.mysql.pymysql")
    def test_get_columns(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("id", "int", "NO", "PRI", None),
            ("name", "varchar", "YES", "", None),
            ("email", "varchar", "YES", "", "'unknown'"),
        ]
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        columns = adapter.get_columns("users")

        assert len(columns) == 3
        assert columns[0] == ColumnInfo(
            name="id", data_type="int", nullable=False, primary_key=True, default=None
        )
        assert columns[1] == ColumnInfo(
            name="name", data_type="varchar", nullable=True, primary_key=False
        )
        assert columns[2] == ColumnInfo(
            name="email",
            data_type="varchar",
            nullable=True,
            primary_key=False,
            default="'unknown'",
        )

    def test_get_columns_not_connected(self, adapter):
        columns = adapter.get_columns("users")
        assert columns == []


class TestMySQLGetDatabases:

    @patch("qry.domains.database.mysql.pymysql")
    def test_get_databases(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("mysql",), ("testdb",)]
        mock_connection.cursor.return_value = mock_cursor

        adapter.connect()
        databases = adapter.get_databases()

        assert databases == ["mysql", "testdb"]

    def test_get_databases_not_connected(self, adapter):
        databases = adapter.get_databases()
        assert databases == []


class TestMySQLCancel:

    @patch("qry.domains.database.mysql.pymysql")
    def test_cancel(self, mock_pymysql, adapter, mock_connection):
        mock_pymysql.connect.return_value = mock_connection

        adapter.connect()
        adapter.cancel()

        mock_connection.kill.assert_called_once_with(mock_connection.thread_id())

    def test_cancel_not_connected(self, adapter):
        adapter.cancel()


class TestMySQLIsConnected:

    def test_not_connected_initially(self, adapter):
        assert not adapter.is_connected()

    @patch("qry.domains.database.mysql.pymysql")
    def test_connected_after_connect(self, mock_pymysql, adapter):
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_pymysql.connect.return_value = mock_conn

        adapter.connect()
        assert adapter.is_connected()

    @patch("qry.domains.database.mysql.pymysql")
    def test_not_connected_when_conn_closed(self, mock_pymysql, adapter):
        mock_conn = MagicMock()
        mock_conn.open = False
        mock_pymysql.connect.return_value = mock_conn

        adapter.connect()
        assert not adapter.is_connected()
