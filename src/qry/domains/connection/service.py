"""Connection manager service."""

from qry.domains.connection.models import ConnectionConfig
from qry.domains.connection.repository import ConnectionRepository
from qry.infrastructure.repositories.yaml_connection import YamlConnectionRepository


class ConnectionManager:
    """Manages database connection configurations.

    Uses repository pattern for persistence, allowing different
    storage backends (YAML, database, etc.)
    """

    def __init__(self, repository: ConnectionRepository | None = None) -> None:
        self._repository = repository or YamlConnectionRepository()
        self._connections: dict[str, ConnectionConfig] = {}
        self._load()

    def _load(self) -> None:
        for conn in self._repository.load_all():
            self._connections[conn.name] = conn

    def save(self) -> None:
        self._repository.save_all(list(self._connections.values()))

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
