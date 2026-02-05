"""Tests for AdapterFactory."""

import pytest

from qry.connection.config import ConnectionConfig, DatabaseType
from qry.database.factory import AdapterFactory
from qry.database.sqlite import SQLiteAdapter


class TestAdapterFactory:
    """Tests for AdapterFactory."""

    def test_create_sqlite_adapter(self, sample_sqlite_db):
        """Test creating SQLite adapter."""
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=str(sample_sqlite_db),
        )

        adapter = AdapterFactory.create(config)

        assert isinstance(adapter, SQLiteAdapter)

    def test_create_sqlite_without_path_raises_error(self):
        """Test SQLite without path raises ValueError."""
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=None,
        )

        with pytest.raises(ValueError, match="path"):
            AdapterFactory.create(config)

    def test_supported_types(self):
        """Test supported_types returns all types."""
        types = AdapterFactory.supported_types()

        assert DatabaseType.SQLITE in types
        assert DatabaseType.POSTGRES in types
        assert DatabaseType.MYSQL in types

    def test_is_available_sqlite(self):
        """Test SQLite is always available."""
        assert AdapterFactory.is_available(DatabaseType.SQLITE) is True
