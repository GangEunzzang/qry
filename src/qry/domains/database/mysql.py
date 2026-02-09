"""MySQL database adapter using PyMySQL."""

import contextlib
import time

import pymysql

from qry.domains.database.base import DatabaseAdapter
from qry.shared.exceptions import DatabaseError
from qry.shared.models import QueryResult
from qry.shared.types import ColumnInfo, IndexInfo, TableInfo, ViewInfo


class MySQLAdapter(DatabaseAdapter):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        database: str = "",
        user: str = "",
        password: str = "",
    ) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._conn: pymysql.Connection | None = None

    def connect(self) -> None:
        try:
            self._conn = pymysql.connect(
                host=self._host,
                port=self._port,
                database=self._database,
                user=self._user,
                password=self._password,
                autocommit=True,
            )
        except pymysql.Error as e:
            raise DatabaseError(
                f"Failed to connect to {self._host}:{self._port}/{self._database}: {e}"
            ) from e

    def disconnect(self) -> None:
        if self._conn and self._conn.open:
            self._conn.close()
        self._conn = None

    def is_connected(self) -> bool:
        return self._conn is not None and self._conn.open

    def execute(self, sql: str) -> QueryResult:
        if not self.is_connected():
            return QueryResult(error="Not connected to database")

        start_time = time.perf_counter()

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute(sql)
                execution_time_ms = (time.perf_counter() - start_time) * 1000

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return QueryResult(
                        columns=columns,
                        rows=[tuple(row) for row in rows],
                        row_count=len(rows),
                        execution_time_ms=execution_time_ms,
                    )
                else:
                    return QueryResult(
                        columns=[],
                        rows=[],
                        row_count=cursor.rowcount if cursor.rowcount >= 0 else 0,
                        execution_time_ms=execution_time_ms,
                    )
        except pymysql.Error as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            return QueryResult(
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    def get_tables(self) -> list[TableInfo]:
        if not self.is_connected():
            return []

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() ORDER BY table_name"
                )
                return [TableInfo(name=row[0]) for row in cursor.fetchall()]
        except pymysql.Error:
            return []

    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        if not self.is_connected():
            return []

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute(
                    "SELECT column_name, data_type, is_nullable, column_key, "
                    "column_default, character_maximum_length "
                    "FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name = %s "
                    "ORDER BY ordinal_position",
                    (table_name,),
                )
                columns = []
                for row in cursor.fetchall():
                    columns.append(
                        ColumnInfo(
                            name=row[0],
                            data_type=row[1],
                            nullable=row[2] == "YES",
                            primary_key=row[3] == "PRI",
                            default=row[4],
                            length=row[5],
                        )
                    )
                return columns
        except pymysql.Error:
            return []

    def get_views(self) -> list[ViewInfo]:
        if not self.is_connected():
            return []

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute(
                    "SELECT table_name FROM information_schema.views "
                    "WHERE table_schema = DATABASE() ORDER BY table_name"
                )
                return [ViewInfo(name=row[0]) for row in cursor.fetchall()]
        except pymysql.Error as e:
            raise DatabaseError(f"Failed to fetch views: {e}") from e

    def get_indexes(self) -> list[IndexInfo]:
        if not self.is_connected():
            return []

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute(
                    "SELECT DISTINCT index_name, table_name, non_unique "
                    "FROM information_schema.statistics "
                    "WHERE table_schema = DATABASE() "
                    "ORDER BY index_name"
                )
                return [
                    IndexInfo(name=row[0], table_name=row[1], unique=not row[2])
                    for row in cursor.fetchall()
                ]
        except pymysql.Error as e:
            raise DatabaseError(f"Failed to fetch indexes: {e}") from e

    def get_databases(self) -> list[str]:
        if not self.is_connected():
            return []

        try:
            with self._conn.cursor() as cursor:  # type: ignore[union-attr]
                cursor.execute("SHOW DATABASES")
                return [row[0] for row in cursor.fetchall()]
        except pymysql.Error:
            return []

    def cancel(self) -> None:
        if self._conn and self._conn.open:
            with contextlib.suppress(pymysql.Error):
                self._conn.kill(self._conn.thread_id())
