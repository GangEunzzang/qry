"""Application context - centralized dependency management."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qry.connection.config import ConnectionConfig
from qry.connection.manager import ConnectionManager
from qry.database.base import DatabaseAdapter
from qry.database.factory import AdapterFactory
from qry.query.service import QueryService
from qry.settings.config import Settings

if TYPE_CHECKING:
    pass


@dataclass
class AppContext:
    """Application context holding all shared state and services.

    This is the central place for dependency management.
    Created once at app startup and passed to components that need it.

    Example:
        >>> ctx = AppContext.create()
        >>> ctx.connect(connection_config)
        >>> result = ctx.query_service.execute("SELECT 1")
    """

    settings: Settings
    connection_manager: ConnectionManager
    _adapter: DatabaseAdapter | None = field(default=None, init=False)
    _query_service: QueryService | None = field(default=None, init=False)
    _current_connection: ConnectionConfig | None = field(default=None, init=False)

    @classmethod
    def create(cls, settings: Settings | None = None) -> "AppContext":
        """Create application context with default or provided settings.

        Args:
            settings: Optional settings. Loads from file if not provided.

        Returns:
            Initialized AppContext.
        """
        if settings is None:
            settings = Settings.load()

        return cls(
            settings=settings,
            connection_manager=ConnectionManager(),
        )

    def connect(self, config: ConnectionConfig, password: str | None = None) -> None:
        """Connect to a database.

        Args:
            config: Connection configuration.
            password: Optional password (for network databases).

        Raises:
            ConnectionError: If connection fails.
        """
        # Disconnect existing connection
        self.disconnect()

        # Create and connect adapter
        adapter = AdapterFactory.create(config)
        adapter.connect()

        self._adapter = adapter
        self._current_connection = config
        self._query_service = QueryService(
            adapter=adapter,
        )

        # Set connection name for history
        self._query_service.history.set_connection(config.name)

    def disconnect(self) -> None:
        """Disconnect from current database."""
        if self._query_service:
            self._query_service.save_history()

        if self._adapter:
            self._adapter.disconnect()

        self._adapter = None
        self._query_service = None
        self._current_connection = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to a database."""
        return self._adapter is not None and self._adapter.is_connected()

    @property
    def adapter(self) -> DatabaseAdapter | None:
        """Get current database adapter."""
        return self._adapter

    @property
    def query_service(self) -> QueryService | None:
        """Get query service (None if not connected)."""
        return self._query_service

    @property
    def current_connection(self) -> ConnectionConfig | None:
        """Get current connection configuration."""
        return self._current_connection

    def get_connections(self) -> list[ConnectionConfig]:
        """Get all saved connections."""
        return self.connection_manager.list_all()

    def save_connection(self, config: ConnectionConfig) -> None:
        """Save a connection configuration."""
        self.connection_manager.add(config)

    def delete_connection(self, name: str) -> None:
        """Delete a saved connection."""
        self.connection_manager.remove(name)
