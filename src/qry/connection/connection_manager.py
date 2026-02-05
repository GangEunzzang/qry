"""Connection manager for handling multiple database connections."""

from pathlib import Path

import yaml

from qry.connection.connection_config import ConnectionConfig
from qry.settings.settings_paths import get_config_dir


class ConnectionManager:
    """Manages database connection configurations."""

    def __init__(self) -> None:
        self._connections: dict[str, ConnectionConfig] = {}
        self._load()

    def _get_connections_path(self) -> Path:
        return get_config_dir() / "connections.yaml"

    def _load(self) -> None:
        path = self._get_connections_path()
        if not path.exists():
            return

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            data = {}

        for conn_data in data.get("connections", []):
            try:
                conn = ConnectionConfig.from_dict(conn_data)
                self._connections[conn.name] = conn
            except (KeyError, ValueError):
                continue

    def save(self) -> None:
        path = self._get_connections_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {"connections": [conn.to_dict() for conn in self._connections.values()]}

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add(self, config: ConnectionConfig) -> None:
        self._connections[config.name] = config
        self.save()

    def remove(self, name: str) -> None:
        if name in self._connections:
            del self._connections[name]
            self.save()

    def get(self, name: str) -> ConnectionConfig | None:
        return self._connections.get(name)

    def list_all(self) -> list[ConnectionConfig]:
        return list(self._connections.values())
