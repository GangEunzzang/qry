"""Tests for AdapterFactory."""

import pytest

from qry.connection.connection_config import ConnectionConfig, DatabaseType
from qry.database.database_factory import AdapterFactory
from qry.database.database_sqlite import SQLiteAdapter


class TestAdapterFactory:

    def test_create_sqlite_adapter(self, sample_sqlite_db):
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

    def test_supported_types(self):
        types = AdapterFactory.supported_types()

        assert DatabaseType.SQLITE in types
        assert DatabaseType.POSTGRES in types
        assert DatabaseType.MYSQL in types

    def test_is_available_sqlite(self):
        assert AdapterFactory.is_available(DatabaseType.SQLITE) is True
