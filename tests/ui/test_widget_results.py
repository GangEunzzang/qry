"""Tests for ResultsTable clipboard copy."""

import json

import pytest

from qry.shared.models import QueryResult
from qry.ui.widgets.widget_results import ResultsTable


@pytest.fixture
def sample_result() -> QueryResult:
    return QueryResult(
        columns=["id", "name", "email"],
        rows=[
            (1, "Alice", "alice@example.com"),
            (2, "Bob", None),
        ],
        row_count=2,
        execution_time_ms=1.5,
    )


@pytest.fixture
def widget() -> ResultsTable:
    table = ResultsTable()
    return table


class TestGetRowAsJson:
    def test_valid_row(self, widget: ResultsTable, sample_result: QueryResult) -> None:
        widget._result = sample_result
        result = widget._get_row_as_json(0)
        assert result is not None
        parsed = json.loads(result)
        assert parsed == {"id": 1, "name": "Alice", "email": "alice@example.com"}

    def test_row_with_none_value(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        result = widget._get_row_as_json(1)
        assert result is not None
        parsed = json.loads(result)
        assert parsed == {"id": 2, "name": "Bob", "email": None}

    def test_no_result(self, widget: ResultsTable) -> None:
        assert widget._get_row_as_json(0) is None

    def test_negative_index(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_row_as_json(-1) is None

    def test_out_of_bounds_index(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_row_as_json(5) is None

    def test_json_preserves_column_order(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        result = widget._get_row_as_json(0)
        assert result is not None
        assert list(json.loads(result).keys()) == ["id", "name", "email"]

    def test_non_ascii_value(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(
            columns=["name"],
            rows=[("한글 테스트",)],
            row_count=1,
        )
        result = widget._get_row_as_json(0)
        assert result is not None
        assert "한글 테스트" in result


class TestGetCellValue:
    def test_valid_cell(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(0, 0) == "1"
        assert widget._get_cell_value(0, 1) == "Alice"
        assert widget._get_cell_value(0, 2) == "alice@example.com"

    def test_none_cell(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(1, 2) == "NULL"

    def test_no_result(self, widget: ResultsTable) -> None:
        assert widget._get_cell_value(0, 0) is None

    def test_negative_row(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(-1, 0) is None

    def test_negative_col(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(0, -1) is None

    def test_row_out_of_bounds(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(10, 0) is None

    def test_col_out_of_bounds(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        assert widget._get_cell_value(0, 10) is None
