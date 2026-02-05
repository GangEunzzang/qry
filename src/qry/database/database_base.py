"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from qry.core.core_types import ColumnInfo, TableInfo

if TYPE_CHECKING:
    from qry.query.query_result import QueryResult


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""

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
