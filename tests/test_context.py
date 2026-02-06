"""Tests for AppContext."""

import sqlite3
from pathlib import Path

import pytest

from qry.context import AppContext
from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.shared.settings import Settings


class TestAppContext:
    @pytest.fixture
    def context(self, tmp_config_dir: Path) -> AppContext:
        return AppContext.create(settings=Settings())

    def test_create_with_default_settings(self, tmp_config_dir: Path):
        ctx = AppContext.create()

        assert ctx.settings is not None
        assert ctx.connection_manager is not None
        assert not ctx.is_connected

    def test_initially_not_connected(self, context: AppContext):
        assert not context.is_connected
        assert context.adapter is None
        assert context.query_service is None
        assert context.current_connection is None

    def test_connect_sqlite(self, context: AppContext, sample_sqlite_db: Path):
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
        assert context.current_connection is None

    def test_connect_replaces_existing(self, context: AppContext, tmp_path: Path):
        db1 = tmp_path / "db1.db"
        db2 = tmp_path / "db2.db"

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

    def test_query_execution_through_context(self, context: AppContext, sample_sqlite_db: Path):
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path=str(sample_sqlite_db),
        )
        context.connect(config)

        result = context.query_service.execute("SELECT * FROM users")

        assert result.is_success
        assert result.row_count == 2

        context.disconnect()

    def test_get_connections(self, context: AppContext):
        connections = context.get_connections()

        assert isinstance(connections, list)

    def test_save_connection(self, context: AppContext):
        config = ConnectionConfig(
            name="saved",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )

        context.save_connection(config)

        connections = context.get_connections()
        names = [c.name for c in connections]
        assert "saved" in names

    def test_delete_connection(self, context: AppContext):
        config = ConnectionConfig(
            name="to_delete",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )
        context.save_connection(config)

        context.delete_connection("to_delete")

        connections = context.get_connections()
        names = [c.name for c in connections]
        assert "to_delete" not in names
