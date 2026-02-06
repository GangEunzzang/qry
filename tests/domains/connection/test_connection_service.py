"""Tests for ConnectionManager service."""

from pathlib import Path

import pytest

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.connection.service import ConnectionManager


class TestConnectionManager:
    @pytest.fixture
    def manager(self, tmp_config_dir: Path) -> ConnectionManager:
        """Create a fresh ConnectionManager with clean config dir."""
        # Clear any existing connections file
        connections_file = tmp_config_dir / "connections.yaml"
        if connections_file.exists():
            connections_file.unlink()
        return ConnectionManager()

    def test_initially_empty(self, manager: ConnectionManager):
        connections = manager.list_all()

        assert connections == []

    def test_add_connection(self, manager: ConnectionManager):
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )

        manager.add(config)

        assert len(manager.list_all()) == 1
        assert manager.get("test") == config

    def test_get_nonexistent(self, manager: ConnectionManager):
        result = manager.get("nonexistent")

        assert result is None

    def test_remove_connection(self, manager: ConnectionManager):
        config = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )
        manager.add(config)

        manager.remove("test")

        assert manager.get("test") is None
        assert len(manager.list_all()) == 0

    def test_remove_nonexistent_no_error(self, manager: ConnectionManager):
        manager.remove("nonexistent")  # Should not raise

    def test_persistence(self, tmp_config_dir: Path):
        # Clear any existing connections file first
        connections_file = tmp_config_dir / "connections.yaml"
        if connections_file.exists():
            connections_file.unlink()

        config = ConnectionConfig(
            name="persistent",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )

        manager1 = ConnectionManager()
        manager1.add(config)

        manager2 = ConnectionManager()
        restored = manager2.get("persistent")

        assert restored is not None
        assert restored.name == "persistent"
        assert restored.path == "/path/to/db.sqlite"

    def test_update_existing(self, manager: ConnectionManager):
        config1 = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db1.sqlite",
        )
        config2 = ConnectionConfig(
            name="test",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db2.sqlite",
        )

        manager.add(config1)
        manager.add(config2)

        assert len(manager.list_all()) == 1
        assert manager.get("test").path == "/path/to/db2.sqlite"

    def test_multiple_connections(self, manager: ConnectionManager):
        configs = [
            ConnectionConfig(name="db1", db_type=DatabaseType.SQLITE, path="/db1.sqlite"),
            ConnectionConfig(name="db2", db_type=DatabaseType.SQLITE, path="/db2.sqlite"),
            ConnectionConfig(name="db3", db_type=DatabaseType.POSTGRES, host="localhost"),
        ]

        for config in configs:
            manager.add(config)

        assert len(manager.list_all()) == 3
        assert manager.get("db1") is not None
        assert manager.get("db2") is not None
        assert manager.get("db3") is not None
