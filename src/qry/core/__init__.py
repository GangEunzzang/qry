"""Core module - shared types, exceptions, and constants."""

from qry.core.constants import APP_NAME, VERSION
from qry.core.exceptions import ConnectionError, QryError, QueryError
from qry.core.types import ColumnInfo, TableInfo

# Note: AppContext is not exported here to avoid circular imports
# Import it directly: from qry.core.context import AppContext

__all__ = [
    "APP_NAME",
    "VERSION",
    "QryError",
    "ConnectionError",
    "QueryError",
    "TableInfo",
    "ColumnInfo",
]
