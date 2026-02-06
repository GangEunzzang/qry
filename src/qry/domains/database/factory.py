"""Database adapter factory."""

from collections.abc import Callable
from typing import ClassVar

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.database.base import DatabaseAdapter

# Type aliases for registry
AdapterCreator = Callable[[ConnectionConfig], DatabaseAdapter]
AvailabilityChecker = Callable[[], bool]


def _check_sqlite() -> bool:
    return True


def _check_postgres() -> bool:
    try:
        import psycopg  # noqa: F401

        return True
    except ImportError:
        return False


def _check_mysql() -> bool:
    try:
        import pymysql  # noqa: F401

        return True
    except ImportError:
        return False


class AdapterFactory:
    """Factory for creating database adapters using registry pattern."""

    _creators: ClassVar[dict[DatabaseType, AdapterCreator]] = {}
    _availability: ClassVar[dict[DatabaseType, AvailabilityChecker]] = {
        DatabaseType.SQLITE: _check_sqlite,
        DatabaseType.POSTGRES: _check_postgres,
        DatabaseType.MYSQL: _check_mysql,
    }

    @classmethod
    def register(cls, db_type: DatabaseType, creator: AdapterCreator) -> None:
        """Register a new adapter creator for a database type."""
        cls._creators[db_type] = creator

    @classmethod
    def create(cls, config: ConnectionConfig) -> DatabaseAdapter:
        creator = cls._creators.get(config.db_type)
        if not creator:
            raise ValueError(f"Unsupported database type: {config.db_type}")
        return creator(config)

    @classmethod
    def supported_types(cls) -> list[DatabaseType]:
        return list(cls._creators.keys())

    @classmethod
    def is_available(cls, db_type: DatabaseType) -> bool:
        checker = cls._availability.get(db_type)
        return checker() if checker else False


# --- Adapter Creators ---


def _create_sqlite(config: ConnectionConfig) -> DatabaseAdapter:
    from qry.domains.database.sqlite import SQLiteAdapter

    if not config.path:
        raise ValueError("SQLite requires 'path' in configuration")
    return SQLiteAdapter(config.path)


def _create_postgres(config: ConnectionConfig) -> DatabaseAdapter:
    raise ImportError(
        "PostgreSQL support requires 'psycopg'. Install with: pip install 'qry[postgres]'"
    )


def _create_mysql(config: ConnectionConfig) -> DatabaseAdapter:
    raise ImportError("MySQL support requires 'pymysql'. Install with: pip install 'qry[mysql]'")


# --- Register adapters ---
AdapterFactory.register(DatabaseType.SQLITE, _create_sqlite)
AdapterFactory.register(DatabaseType.POSTGRES, _create_postgres)
AdapterFactory.register(DatabaseType.MYSQL, _create_mysql)
