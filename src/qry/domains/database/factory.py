"""Database adapter factory."""

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.database.base import DatabaseAdapter


class AdapterFactory:
    """Factory for creating database adapters."""

    @classmethod
    def create(cls, config: ConnectionConfig) -> DatabaseAdapter:
        if config.db_type == DatabaseType.SQLITE:
            return cls._create_sqlite(config)
        elif config.db_type == DatabaseType.POSTGRES:
            return cls._create_postgres(config)
        elif config.db_type == DatabaseType.MYSQL:
            return cls._create_mysql(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")

    @classmethod
    def _create_sqlite(cls, config: ConnectionConfig) -> DatabaseAdapter:
        from qry.domains.database.sqlite import SQLiteAdapter

        if not config.path:
            raise ValueError("SQLite requires 'path' in configuration")
        return SQLiteAdapter(config.path)

    @classmethod
    def _create_postgres(cls, config: ConnectionConfig) -> DatabaseAdapter:
        raise ImportError(
            "PostgreSQL support requires 'psycopg'. Install with: pip install 'qry[postgres]'"
        )

    @classmethod
    def _create_mysql(cls, config: ConnectionConfig) -> DatabaseAdapter:
        raise ImportError(
            "MySQL support requires 'pymysql'. Install with: pip install 'qry[mysql]'"
        )

    @classmethod
    def supported_types(cls) -> list[DatabaseType]:
        return [DatabaseType.SQLITE, DatabaseType.POSTGRES, DatabaseType.MYSQL]

    @classmethod
    def is_available(cls, db_type: DatabaseType) -> bool:
        if db_type == DatabaseType.SQLITE:
            return True
        elif db_type == DatabaseType.POSTGRES:
            try:
                import psycopg  # noqa: F401

                return True
            except ImportError:
                return False
        elif db_type == DatabaseType.MYSQL:
            try:
                import pymysql  # noqa: F401

                return True
            except ImportError:
                return False
        return False
