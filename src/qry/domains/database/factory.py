"""Database adapter factory."""

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.database.base import DatabaseAdapter


def _try_import(module: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False


class AdapterFactory:
    """Factory for creating database adapters."""

    # Module requirements for each database type
    _REQUIRED_MODULES = {
        DatabaseType.POSTGRES: "psycopg",
        DatabaseType.MYSQL: "pymysql",
    }

    @classmethod
    def create(cls, config: ConnectionConfig) -> DatabaseAdapter:
        """Create adapter for the given configuration."""
        match config.db_type:
            case DatabaseType.SQLITE:
                return cls._create_sqlite(config)
            case DatabaseType.POSTGRES:
                return cls._create_postgres(config)
            case DatabaseType.MYSQL:
                return cls._create_mysql(config)
            case _:
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
        """Get list of all supported database types."""
        return list(DatabaseType)

    @classmethod
    def is_available(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is available (dependencies installed)."""
        if db_type == DatabaseType.SQLITE:
            return True  # Built-in, always available
        module = cls._REQUIRED_MODULES.get(db_type)
        return _try_import(module) if module else False
