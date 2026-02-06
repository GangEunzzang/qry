"""Application context - centralized dependency management."""

from dataclasses import dataclass, field

from qry.domains.connection.models import ConnectionConfig
from qry.domains.connection.service import ConnectionManager
from qry.domains.database.base import DatabaseAdapter
from qry.domains.database.factory import AdapterFactory
from qry.domains.query.service import QueryService
from qry.shared.settings import Settings


@dataclass
class AppContext:
    """Application context holding all shared state and services."""

    settings: Settings
    connection_manager: ConnectionManager
    _adapter: DatabaseAdapter | None = field(default=None, init=False)
    _query_service: QueryService | None = field(default=None, init=False)
    _current_connection: ConnectionConfig | None = field(default=None, init=False)

    @classmethod
    def create(cls, settings: Settings | None = None) -> "AppContext":
        if settings is None:
            settings = Settings.load()
        return cls(
            settings=settings,
            connection_manager=ConnectionManager(),
        )

    def connect(self, config: ConnectionConfig) -> None:
        self.disconnect()
        adapter = AdapterFactory.create(config)
        adapter.connect()

        try:
            self._adapter = adapter
            self._current_connection = config
            self._query_service = QueryService(adapter=adapter)
            self._query_service.history.set_connection(config.name)
        except Exception:
            adapter.disconnect()
            self._adapter = None
            self._current_connection = None
            self._query_service = None
            raise

    def disconnect(self) -> None:
        try:
            if self._query_service:
                self._query_service.save_history()
        finally:
            if self._adapter:
                self._adapter.disconnect()
            self._adapter = None
            self._query_service = None
            self._current_connection = None

    @property
    def is_connected(self) -> bool:
        return self._adapter is not None and self._adapter.is_connected()

    @property
    def adapter(self) -> DatabaseAdapter | None:
        return self._adapter

    @property
    def query_service(self) -> QueryService | None:
        return self._query_service

    @property
    def current_connection(self) -> ConnectionConfig | None:
        return self._current_connection

    def get_connections(self) -> list[ConnectionConfig]:
        return self.connection_manager.list_all()

    def save_connection(self, config: ConnectionConfig) -> None:
        self.connection_manager.add(config)

    def delete_connection(self, name: str) -> None:
        self.connection_manager.remove(name)
