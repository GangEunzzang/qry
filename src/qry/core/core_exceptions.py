"""Custom exceptions for qry."""


class QryError(Exception):
    """Base exception for qry."""
    pass


class ConnectionError(QryError):
    """Database connection error."""
    pass


class QueryError(QryError):
    """Query execution error."""

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position
