"""Tests for connection models."""

import pytest

from qry.domains.connection.models import ConnectionConfig, DatabaseType


class TestDatabaseType:
    def test_sqlite_value(self):
        assert DatabaseType.SQLITE.value == "sqlite"

    def test_postgres_value(self):
        assert DatabaseType.POSTGRES.value == "postgres"

    def test_mysql_value(self):
        assert DatabaseType.MYSQL.value == "mysql"


class TestConnectionConfig:
    def test_sqlite_config(self):
        config = ConnectionConfig(
            name="local",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )

        assert config.name == "local"
        assert config.db_type == DatabaseType.SQLITE
        assert config.path == "/path/to/db.sqlite"
        assert config.host is None

    def test_postgres_config(self):
        config = ConnectionConfig(
            name="production",
            db_type=DatabaseType.POSTGRES,
            host="localhost",
            port=5432,
            database="mydb",
            user="admin",
        )

        assert config.name == "production"
        assert config.db_type == DatabaseType.POSTGRES
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "mydb"
        assert config.user == "admin"

    def test_to_dict_sqlite(self):
        config = ConnectionConfig(
            name="local",
            db_type=DatabaseType.SQLITE,
            path="/path/to/db.sqlite",
        )

        data = config.to_dict()

        assert data == {
            "name": "local",
            "type": "sqlite",
            "path": "/path/to/db.sqlite",
        }

    def test_to_dict_postgres(self):
        config = ConnectionConfig(
            name="prod",
            db_type=DatabaseType.POSTGRES,
            host="localhost",
            port=5432,
            database="mydb",
            user="admin",
        )

        data = config.to_dict()

        assert data["name"] == "prod"
        assert data["type"] == "postgres"
        assert data["host"] == "localhost"
        assert data["port"] == 5432
        assert data["database"] == "mydb"
        assert data["user"] == "admin"
        assert "path" not in data

    def test_from_dict_sqlite(self):
        data = {
            "name": "local",
            "type": "sqlite",
            "path": "/path/to/db.sqlite",
        }

        config = ConnectionConfig.from_dict(data)

        assert config.name == "local"
        assert config.db_type == DatabaseType.SQLITE
        assert config.path == "/path/to/db.sqlite"

    def test_from_dict_postgres(self):
        data = {
            "name": "prod",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "admin",
        }

        config = ConnectionConfig.from_dict(data)

        assert config.name == "prod"
        assert config.db_type == DatabaseType.POSTGRES
        assert config.host == "localhost"
        assert config.port == 5432

    def test_roundtrip(self):
        original = ConnectionConfig(
            name="test",
            db_type=DatabaseType.POSTGRES,
            host="localhost",
            port=5432,
            database="testdb",
            user="tester",
        )

        data = original.to_dict()
        restored = ConnectionConfig.from_dict(data)

        assert restored.name == original.name
        assert restored.db_type == original.db_type
        assert restored.host == original.host
        assert restored.port == original.port
        assert restored.database == original.database
        assert restored.user == original.user
