"""Query domain ports (interfaces for external dependencies)."""

from abc import ABC, abstractmethod

from qry.shared.types import ColumnInfo, TableInfo


class SchemaProvider(ABC):
    """Port for accessing database schema information.

    This abstraction allows the query domain to access schema data
    without depending on the database domain directly.
    """

    @abstractmethod
    def get_tables(self) -> list[TableInfo]:
        """Get list of tables in the database."""
        pass

    @abstractmethod
    def get_columns(self, table_name: str) -> list[ColumnInfo]:
        """Get columns for a specific table."""
        pass
