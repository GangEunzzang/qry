"""SQLite database adapter."""

import sqlite3
import time
from pathlib import Path

from qry.core.exceptions import ConnectionError
from qry.core.types import ColumnInfo, TableInfo
from qry.database.base import DatabaseAdapter
from qry.query.result import QueryResult


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter."""

    def __init__(self, path: str | Path) -> None:
        """Initialize SQLite adapter.

        Args:
            path: Path to SQLite database file.
        """
        self._path = Path(path).expanduser()
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to SQLite database."""
        try:
            self._conn = sqlite3.connect(str(self._path))
            self._conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to {self._path}: {e}") from e

    def disconnect(self) -> None:
        """Disconnect from SQLite database."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._conn is not None

    def execute(self, sql: str) -> QueryResult:
        """Execute SQL query."""
        if not self._conn:
            return QueryResult(error="Not connected to database")

        start_time = time.perf_counter()

        try:
            cursor = self._conn.execute(sql)
            rows = cursor.fetchall()

            execution_time_ms = (time.perf_counter() - start_time) * 1000

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                return QueryResult(
                    columns=columns,
                    rows=[tuple(row) for row in rows],
                    row_count=len(rows),
                    execution_time_ms=execution_time_ms,
                )
            else:
                # Non-SELECT statement
                self._conn.commit()
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=cursor.rowcount,
                    execution_time_ms=execution_time_ms,
                )

        except sqlite3.Error as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            return QueryResult(
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    def get_tables(self) -> list[TableInfo]:
        """Get list of tables."""
        if not self._conn:
            return []

        cursor = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [TableInfo(name=row[0]) for row in cursor.fetchall()]

    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        """Get columns for a table."""
        if not self._conn:
            return []

        cursor = self._conn.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append(
                ColumnInfo(
                    name=row[1],
                    data_type=row[2],
                    nullable=not row[3],
                    primary_key=bool(row[5]),
                    default=row[4],
                )
            )
        return columns

    def get_databases(self) -> list[str]:
        """Get list of databases (attached databases for SQLite)."""
        if not self._conn:
            return []

        cursor = self._conn.execute("PRAGMA database_list")
        return [row[1] for row in cursor.fetchall()]

    def cancel(self) -> None:
        """Cancel running query by interrupting connection."""
        if self._conn:
            self._conn.interrupt()
