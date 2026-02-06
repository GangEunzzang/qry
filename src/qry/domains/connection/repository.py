"""Connection repository abstraction."""

from abc import ABC, abstractmethod

from qry.domains.connection.models import ConnectionConfig


class ConnectionRepository(ABC):
    """Abstract repository for connection configurations.

    Implementations handle the actual persistence mechanism
    (YAML files, database, etc.)
    """

    @abstractmethod
    def load_all(self) -> list[ConnectionConfig]:
        """Load all connection configurations."""
        pass

    @abstractmethod
    def save_all(self, configs: list[ConnectionConfig]) -> None:
        """Save all connection configurations."""
        pass
