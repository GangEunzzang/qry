"""Connection domain models."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DatabaseType(str, Enum):
    """Supported database types with their metadata."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"

    @property
    def required_module(self) -> str | None:
        """Module that must be installed to use this database type."""
        return {
            DatabaseType.POSTGRES: "psycopg",
            DatabaseType.MYSQL: "pymysql",
        }.get(self)

    @property
    def install_hint(self) -> str | None:
        """Pip install command for this database type."""
        return {
            DatabaseType.POSTGRES: "pip install 'qry[postgres]'",
            DatabaseType.MYSQL: "pip install 'qry[mysql]'",
        }.get(self)

    def is_available(self) -> bool:
        """Check if required dependencies are installed."""
        if self.required_module is None:
            return True
        try:
            __import__(self.required_module)
            return True
        except ImportError:
            return False


@dataclass
class ConnectionConfig:
    name: str
    db_type: DatabaseType
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
    password: str | None = None
    path: str | None = None  # SQLite specific

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "type": self.db_type.value,
        }

        if self.db_type == DatabaseType.SQLITE:
            if self.path:
                data["path"] = self.path
        else:
            if self.host:
                data["host"] = self.host
            if self.port:
                data["port"] = self.port
            if self.database:
                data["database"] = self.database
            if self.user:
                data["user"] = self.user

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConnectionConfig":
        db_type = DatabaseType(data["type"])
        return cls(
            name=data["name"],
            db_type=db_type,
            host=data.get("host"),
            port=data.get("port"),
            database=data.get("database"),
            user=data.get("user"),
            path=data.get("path"),
        )
