"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from qry.domains.query.ports import SchemaProvider
from qry.shared.types import ColumnInfo, IndexInfo, TableInfo, ViewInfo

if TYPE_CHECKING:
    from qry.shared.models import QueryResult


class DatabaseAdapter(SchemaProvider, ABC):
    """Abstract base class for database adapters.

    Implements SchemaProvider to allow query domain to access schema
    without direct dependency on database domain.
    """

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def execute(self, sql: str) -> "QueryResult":
        pass

    @abstractmethod
    def get_tables(self) -> list[TableInfo]:
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        pass

    @abstractmethod
    def get_databases(self) -> list[str]:
        pass

    def get_views(self) -> list[ViewInfo]:
        return []

    def get_indexes(self) -> list[IndexInfo]:
        return []

    def test_connection(self) -> tuple[bool, str]:
        """Test database connection. Returns (success, message)."""
        try:
            was_connected = self.is_connected()
            if not was_connected:
                self.connect()

            result = self.execute("SELECT 1")

            if not was_connected:
                self.disconnect()

            if result.is_success:
                return True, "Connection successful"
            return False, result.error or "Unknown error"
        except Exception as e:
            return False, str(e)

    def cancel(self) -> None:
        pass
