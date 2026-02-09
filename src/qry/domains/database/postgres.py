"""PostgreSQL database adapter using psycopg v3."""

import time

import psycopg

from qry.domains.database.base import DatabaseAdapter
from qry.shared.exceptions import DatabaseError
from qry.shared.models import QueryResult
from qry.shared.types import ColumnInfo, IndexInfo, TableInfo, ViewInfo


class PostgresAdapter(DatabaseAdapter):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "",
        user: str = "",
        password: str = "",
    ) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._conn: psycopg.Connection | None = None

    def connect(self) -> None:
        try:
            self._conn = psycopg.connect(
                host=self._host,
                port=self._port,
                dbname=self._database,
                user=self._user,
                password=self._password,
                autocommit=True,
            )
        except psycopg.Error as e:
            raise DatabaseError(
                f"Failed to connect to {self._host}:{self._port}/{self._database}: {e}"
            ) from e

    def disconnect(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()
        self._conn = None

    def is_connected(self) -> bool:
        return self._conn is not None and not self._conn.closed

    def execute(self, sql: str) -> QueryResult:
        if not self.is_connected():
            return QueryResult(error="Not connected to database")

        start_time = time.perf_counter()

        try:
            cursor = self._conn.execute(sql)  # type: ignore[union-attr]
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

        except psycopg.Error as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            return QueryResult(
                error=str(e),
                execution_time_ms=execution_time_ms,
            )

    def get_tables(self) -> list[TableInfo]:
        if not self.is_connected():
            return []

        try:
            cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            return [TableInfo(name=row[0], schema="public") for row in cursor.fetchall()]
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to fetch tables: {e}") from e

    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        if not self.is_connected():
            return []

        try:
            cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT column_name, data_type, is_nullable, column_default, "
                "character_maximum_length "
                "FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = %s "
                "ORDER BY ordinal_position",
                (table_name,),
            )

            pk_cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT a.attname "
                "FROM pg_index i "
                "JOIN pg_attribute a ON a.attrelid = i.indrelid "
                "AND a.attnum = ANY(i.indkey) "
                "WHERE i.indrelid = %s::regclass AND i.indisprimary",
                (table_name,),
            )
            pk_columns = {row[0] for row in pk_cursor.fetchall()}
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to fetch columns: {e}") from e

        columns = []
        for row in cursor.fetchall():
            columns.append(
                ColumnInfo(
                    name=row[0],
                    data_type=row[1],
                    nullable=row[2] == "YES",
                    primary_key=row[0] in pk_columns,
                    default=row[3],
                    length=row[4],
                )
            )
        return columns

    def get_views(self) -> list[ViewInfo]:
        if not self.is_connected():
            return []

        try:
            cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT table_name FROM information_schema.views "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            return [ViewInfo(name=row[0], schema="public") for row in cursor.fetchall()]
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to fetch views: {e}") from e

    def get_indexes(self) -> list[IndexInfo]:
        if not self.is_connected():
            return []

        try:
            cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT indexname, tablename, "
                "NOT indisunique AS non_unique "
                "FROM pg_indexes i "
                "JOIN pg_class c ON c.relname = i.indexname "
                "JOIN pg_index ix ON ix.indexrelid = c.oid "
                "WHERE i.schemaname = 'public' "
                "ORDER BY indexname"
            )
            return [
                IndexInfo(name=row[0], table_name=row[1], unique=not row[2], schema="public")
                for row in cursor.fetchall()
            ]
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to fetch indexes: {e}") from e

    def get_databases(self) -> list[str]:
        if not self.is_connected():
            return []

        try:
            cursor = self._conn.execute(  # type: ignore[union-attr]
                "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
            )
            return [row[0] for row in cursor.fetchall()]
        except psycopg.Error as e:
            raise DatabaseError(f"Failed to fetch databases: {e}") from e

    def cancel(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.cancel()
