"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from qry.domains.query.ports import SchemaProvider
from qry.shared.types import ColumnInfo, TableInfo

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

    def cancel(self) -> None:
        pass
