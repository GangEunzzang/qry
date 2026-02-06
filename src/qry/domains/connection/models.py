"""Connection domain models."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    MYSQL = "mysql"


@dataclass
class ConnectionConfig:
    name: str
    db_type: DatabaseType
    host: str | None = None
    port: int | None = None
    database: str | None = None
    user: str | None = None
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
