"""Database adapter factory."""

from typing import TYPE_CHECKING

from qry.connection.config import ConnectionConfig, DatabaseType
from qry.database.base import DatabaseAdapter

if TYPE_CHECKING:
    pass


class AdapterFactory:
    """Factory for creating database adapters.

    Centralizes adapter creation logic and makes it easy to add new adapters.

    Example:
        >>> config = ConnectionConfig(name="test", db_type=DatabaseType.SQLITE, path="test.db")
        >>> adapter = AdapterFactory.create(config)
        >>> adapter.connect()
    """

    @classmethod
    def create(cls, config: ConnectionConfig) -> DatabaseAdapter:
        """Create a database adapter for the given configuration.

        Args:
            config: Connection configuration.

        Returns:
            Database adapter instance (not connected).

        Raises:
            ValueError: If database type is not supported.
        """
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
        """Create SQLite adapter."""
        from qry.database.sqlite import SQLiteAdapter

        if not config.path:
            raise ValueError("SQLite requires 'path' in configuration")
        return SQLiteAdapter(config.path)

    @classmethod
    def _create_postgres(cls, config: ConnectionConfig) -> DatabaseAdapter:
        """Create PostgreSQL adapter."""
        # Lazy import to avoid loading psycopg if not needed
        try:
            from qry.database.postgres import PostgresAdapter
        except ImportError as e:
            raise ImportError(
                "PostgreSQL support requires 'psycopg'. "
                "Install with: pip install 'qry[postgres]'"
            ) from e

        return PostgresAdapter(
            host=config.host or "localhost",
            port=config.port or 5432,
            database=config.database or "",
            user=config.user or "",
        )

    @classmethod
    def _create_mysql(cls, config: ConnectionConfig) -> DatabaseAdapter:
        """Create MySQL adapter."""
        try:
            from qry.database.mysql import MySQLAdapter
        except ImportError as e:
            raise ImportError(
                "MySQL support requires 'pymysql'. "
                "Install with: pip install 'qry[mysql]'"
            ) from e

        return MySQLAdapter(
            host=config.host or "localhost",
            port=config.port or 3306,
            database=config.database or "",
            user=config.user or "",
        )

    @classmethod
    def supported_types(cls) -> list[DatabaseType]:
        """Get list of supported database types.

        Returns:
            List of supported DatabaseType values.
        """
        return [DatabaseType.SQLITE, DatabaseType.POSTGRES, DatabaseType.MYSQL]

    @classmethod
    def is_available(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is available (driver installed).

        Args:
            db_type: Database type to check.

        Returns:
            True if the driver is installed.
        """
        if db_type == DatabaseType.SQLITE:
            return True  # Built-in
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
