"""Tests for shared exceptions."""

import pytest

from qry.shared.exceptions import (
    DatabaseError,
    ExportError,
    OperationCancelled,
    QueryError,
    QryError,
)


class TestExceptionHierarchy:
    def test_qry_error_is_exception(self):
        assert issubclass(QryError, Exception)

    def test_database_error_is_qry_error(self):
        assert issubclass(DatabaseError, QryError)

    def test_query_error_is_qry_error(self):
        assert issubclass(QueryError, QryError)

    def test_export_error_is_qry_error(self):
        assert issubclass(ExportError, QryError)

    def test_operation_cancelled_is_qry_error(self):
        assert issubclass(OperationCancelled, QryError)


class TestQryError:
    def test_message(self):
        error = QryError("Something went wrong")

        assert str(error) == "Something went wrong"

    def test_catch_as_exception(self):
        with pytest.raises(Exception):
            raise QryError("test")


class TestQueryError:
    def test_message(self):
        error = QueryError("Invalid SQL")

        assert str(error) == "Invalid SQL"
        assert error.position is None

    def test_with_position(self):
        error = QueryError("Syntax error", position=42)

        assert str(error) == "Syntax error"
        assert error.position == 42


class TestDatabaseError:
    def test_catch_as_qry_error(self):
        with pytest.raises(QryError):
            raise DatabaseError("Connection failed")


class TestOperationCancelled:
    def test_is_not_regular_error(self):
        """OperationCancelled should be catchable separately."""
        try:
            raise OperationCancelled("User cancelled")
        except OperationCancelled:
            pass  # Expected
        except QryError:
            pytest.fail("Should have been caught as OperationCancelled first")
