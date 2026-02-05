"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from qry.core.types import ColumnInfo, TableInfo

if TYPE_CHECKING:
    from qry.query.result import QueryResult


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the database.

        Returns:
            True if connected, False otherwise.
        """

    @abstractmethod
    def execute(self, sql: str) -> "QueryResult":
        """Execute a SQL query.

        Args:
            sql: SQL query string.

        Returns:
            Query execution result.
        """

    @abstractmethod
    def get_tables(self) -> list[TableInfo]:
        """Get list of tables in the database.

        Returns:
            List of table information.
        """

    @abstractmethod
    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        """Get columns for a specific table.

        Args:
            table_name: Name of the table.

        Returns:
            List of column information.
        """

    @abstractmethod
    def get_databases(self) -> list[str]:
        """Get list of databases (schemas for some DBs).

        Returns:
            List of database names.
        """

    def cancel(self) -> None:
        """Cancel the currently running query.

        Default implementation does nothing.
        Override in adapters that support cancellation.
        """
        pass
