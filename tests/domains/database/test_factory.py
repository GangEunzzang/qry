"""Tests for AdapterFactory."""

from pathlib import Path

import pytest

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.database.factory import AdapterFactory
from qry.domains.database.sqlite import SQLiteAdapter


class TestAdapterFactory:
    def test_create_sqlite_adapter(self, sample_sqlite_db: Path):
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=str(sample_sqlite_db),
        )

        adapter = AdapterFactory.create(config)

        assert isinstance(adapter, SQLiteAdapter)

    def test_create_sqlite_without_path_raises_error(self):
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=None,
        )

        with pytest.raises(ValueError, match="path"):
            AdapterFactory.create(config)

    def test_create_postgres_adapter(self):
        psycopg2 = pytest.importorskip("psycopg2")  # noqa: F841
        from qry.domains.database.postgres import PostgresAdapter

        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.POSTGRES,
            host="localhost",
            database="test",
        )

        adapter = AdapterFactory.create(config)

        assert isinstance(adapter, PostgresAdapter)

    def test_create_mysql_adapter(self):
        pytest.importorskip("pymysql")
        from qry.domains.database.mysql import MySQLAdapter

        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="test",
        )

        adapter = AdapterFactory.create(config)

        assert isinstance(adapter, MySQLAdapter)

    def test_supported_types(self):
        types = AdapterFactory.supported_types()

        assert DatabaseType.SQLITE in types
        assert DatabaseType.POSTGRES in types
        assert DatabaseType.MYSQL in types

    def test_is_available_sqlite(self):
        assert AdapterFactory.is_available(DatabaseType.SQLITE) is True

    def test_is_available_postgres(self):
        # May be True or False depending on environment
        result = AdapterFactory.is_available(DatabaseType.POSTGRES)
        assert isinstance(result, bool)

    def test_is_available_mysql(self):
        # May be True or False depending on environment
        result = AdapterFactory.is_available(DatabaseType.MYSQL)
        assert isinstance(result, bool)
