"""Tests for AppContext."""

from pathlib import Path

import pytest

from qry.connection.config import ConnectionConfig, DatabaseType
from qry.core.context import AppContext
from qry.settings.config import Settings


class TestAppContext:
    """Tests for AppContext."""

    @pytest.fixture
    def context(self) -> AppContext:
        """Create AppContext with default settings."""
        return AppContext.create(settings=Settings())

    def test_create_with_default_settings(self):
        """Test creating context with default settings."""
        ctx = AppContext.create()

        assert ctx.settings is not None
        assert ctx.connection_manager is not None
        assert not ctx.is_connected

    def test_connect_sqlite(self, context: AppContext, sample_sqlite_db: Path):
        """Test connecting to SQLite database."""
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=str(sample_sqlite_db),
        )

        context.connect(config)

        assert context.is_connected
        assert context.adapter is not None
        assert context.query_service is not None
        assert context.current_connection == config

    def test_disconnect(self, context: AppContext, sample_sqlite_db: Path):
        """Test disconnecting from database."""
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=str(sample_sqlite_db),
        )
        context.connect(config)

        context.disconnect()

        assert not context.is_connected
        assert context.adapter is None
        assert context.query_service is None

    def test_connect_replaces_existing(self, context: AppContext, tmp_path: Path):
        """Test that connecting replaces existing connection."""
        # Create two databases
        db1 = tmp_path / "db1.db"
        db2 = tmp_path / "db2.db"

        import sqlite3
        for db in [db1, db2]:
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE test (id INTEGER)")
            conn.close()

        config1 = ConnectionConfig(name="db1", db_type=DatabaseType.SQLITE, path=str(db1))
        config2 = ConnectionConfig(name="db2", db_type=DatabaseType.SQLITE, path=str(db2))

        context.connect(config1)
        assert context.current_connection.name == "db1"

        context.connect(config2)
        assert context.current_connection.name == "db2"
