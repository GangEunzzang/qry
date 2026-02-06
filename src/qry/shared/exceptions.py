"""Custom exceptions for qry."""


class QryError(Exception):
    """Base exception for qry."""

    pass


class DatabaseError(QryError):
    """Database connection or query error."""

    pass


class QueryError(QryError):
    """Query execution error."""

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position


class ExportError(QryError):
    """Export operation error."""

    pass


class OperationCancelled(QryError):
    """User cancelled operation - not an error, normal flow control."""

    pass
