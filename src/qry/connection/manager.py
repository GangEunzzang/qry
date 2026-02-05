"""Connection manager for handling multiple database connections."""

from pathlib import Path

import yaml

from qry.connection.config import ConnectionConfig
from qry.settings.paths import get_config_dir


class ConnectionManager:
    """Manages database connection configurations."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        self._connections: dict[str, ConnectionConfig] = {}
        self._load()

    def _get_connections_path(self) -> Path:
        """Get the connections file path."""
        return get_config_dir() / "connections.yaml"

    def _load(self) -> None:
        """Load connections from file."""
        path = self._get_connections_path()

        if not path.exists():
            return

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        for conn_data in data.get("connections", []):
            conn = ConnectionConfig.from_dict(conn_data)
            self._connections[conn.name] = conn

    def save(self) -> None:
        """Save connections to file."""
        path = self._get_connections_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {"connections": [conn.to_dict() for conn in self._connections.values()]}

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add(self, config: ConnectionConfig) -> None:
        """Add a new connection."""
        self._connections[config.name] = config
        self.save()

    def remove(self, name: str) -> None:
        """Remove a connection by name."""
        if name in self._connections:
            del self._connections[name]
            self.save()

    def get(self, name: str) -> ConnectionConfig | None:
        """Get a connection by name."""
        return self._connections.get(name)

    def list_all(self) -> list[ConnectionConfig]:
        """List all connections."""
        return list(self._connections.values())
