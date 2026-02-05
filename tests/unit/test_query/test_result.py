"""Tests for QueryResult."""

from qry.query.query_result import QueryResult


def test_query_result_success():
    result = QueryResult(
        columns=["id", "name"],
        rows=[(1, "Alice"), (2, "Bob")],
        row_count=2,
        execution_time_ms=5.0,
    )

    assert result.is_success
    assert not result.is_empty
    assert result.row_count == 2


def test_query_result_error():
    result = QueryResult(error="Table not found")

    assert not result.is_success
    assert result.error == "Table not found"


def test_query_result_empty():
    result = QueryResult(
        columns=["id"],
        rows=[],
        row_count=0,
        execution_time_ms=1.0,
    )

    assert result.is_success
    assert result.is_empty
