"""SQLite database adapter."""

import re
import sqlite3
import time
from pathlib import Path

from qry.domains.database.base import DatabaseAdapter
from qry.shared.exceptions import DatabaseError
from qry.shared.models import QueryResult
from qry.shared.types import ColumnInfo, IndexInfo, TableInfo, ViewInfo


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path).expanduser()
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        try:
            self._conn = sqlite3.connect(str(self._path))
            self._conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to {self._path}: {e}") from e

    def disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def is_connected(self) -> bool:
        return self._conn is not None

    def execute(self, sql: str) -> QueryResult:
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
        if not self._conn:
            return []

        try:
            cursor = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            return [TableInfo(name=row[0]) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch tables: {e}") from e

    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        if not self._conn:
            return []

        try:
            safe_name = table_name.replace('"', '""')
            cursor = self._conn.execute(f'PRAGMA table_info("{safe_name}")')
            columns = []
            for row in cursor.fetchall():
                raw_type = row[2] or ""
                data_type, length = self._parse_type_length(raw_type)
                columns.append(
                    ColumnInfo(
                        name=row[1],
                        data_type=data_type,
                        nullable=not row[3],
                        primary_key=bool(row[5]),
                        default=row[4],
                        length=length,
                    )
                )
            return columns
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch columns: {e}") from e

    @staticmethod
    def _parse_type_length(raw_type: str) -> tuple[str, int | None]:
        """Parse type and length from SQLite type string like 'VARCHAR(255)'."""
        match = re.match(r"^\s*([A-Za-z ]+?)\s*\(\s*(\d+)\s*\)", raw_type)
        if match:
            return match.group(1).strip(), int(match.group(2))
        return raw_type.strip(), None

    def get_views(self) -> list[ViewInfo]:
        if not self._conn:
            return []

        try:
            cursor = self._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
            )
            return [ViewInfo(name=row[0]) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch views: {e}") from e

    def get_indexes(self) -> list[IndexInfo]:
        if not self._conn:
            return []

        try:
            cursor = self._conn.execute(
                "SELECT name, tbl_name FROM sqlite_master "
                "WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            indexes = []
            for row in cursor.fetchall():
                safe_table = row[1].replace('"', '""')
                list_cursor = self._conn.execute(f'PRAGMA index_list("{safe_table}")')
                unique = False
                for idx_row in list_cursor.fetchall():
                    if idx_row[1] == row[0]:
                        unique = bool(idx_row[2])
                        break
                indexes.append(IndexInfo(name=row[0], table_name=row[1], unique=unique))
            return indexes
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch indexes: {e}") from e

    def get_databases(self) -> list[str]:
        if not self._conn:
            return []

        try:
            cursor = self._conn.execute("PRAGMA database_list")
            return [row[1] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch databases: {e}") from e

    def cancel(self) -> None:
        if self._conn:
            self._conn.interrupt()
