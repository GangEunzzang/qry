"""Database adapter factory."""

from qry.domains.connection.models import ConnectionConfig, DatabaseType
from qry.domains.database.base import DatabaseAdapter


class AdapterFactory:
    """Factory for creating database adapters."""

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
        try:
            from qry.domains.database.postgres import PostgresAdapter
        except ImportError as e:
            db_type = DatabaseType.POSTGRES
            raise ImportError(
                f"PostgreSQL support requires '{db_type.required_module}'. "
                f"Install with: {db_type.install_hint}"
            ) from e

        return PostgresAdapter(
            host=config.host or "localhost",
            port=config.port or 5432,
            database=config.database or "",
            user=config.user or "",
            password=config.password or "",
        )

    @classmethod
    def _create_mysql(cls, config: ConnectionConfig) -> DatabaseAdapter:
        db_type = DatabaseType.MYSQL
        raise ImportError(
            f"MySQL support requires '{db_type.required_module}'. "
            f"Install with: {db_type.install_hint}"
        )

    @classmethod
    def supported_types(cls) -> list[DatabaseType]:
        """Get list of all supported database types."""
        return list(DatabaseType)

    @classmethod
    def is_available(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is available (dependencies installed)."""
        return db_type.is_available()
