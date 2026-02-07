"""Tests for ResultsTable clipboard copy and column sorting."""

import json
from unittest.mock import MagicMock

import pytest

from qry.shared.models import QueryResult
from qry.ui.widgets.widget_results import ResultsTable, SortDirection


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


class TestColumnLabel:
    def test_no_sort(self, widget: ResultsTable) -> None:
        assert widget._column_label("name", 0) == "name"

    def test_asc_indicator(self, widget: ResultsTable) -> None:
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        assert widget._column_label("name", 0) == "name \u25b2"

    def test_desc_indicator(self, widget: ResultsTable) -> None:
        widget._sort_column = 0
        widget._sort_direction = SortDirection.DESC
        assert widget._column_label("name", 0) == "name \u25bc"

    def test_different_column_no_indicator(self, widget: ResultsTable) -> None:
        widget._sort_column = 1
        widget._sort_direction = SortDirection.ASC
        assert widget._column_label("name", 0) == "name"

    def test_sort_none_no_indicator(self, widget: ResultsTable) -> None:
        widget._sort_column = 0
        widget._sort_direction = SortDirection.NONE
        assert widget._column_label("name", 0) == "name"


class TestSortedRows:
    def test_no_result(self, widget: ResultsTable) -> None:
        assert widget._sorted_rows() == []

    def test_no_sort(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        rows = widget._sorted_rows()
        assert rows == list(sample_result.rows)

    def test_sort_asc_by_name(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        widget._sort_column = 1
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][1] == "Alice"
        assert rows[1][1] == "Bob"

    def test_sort_desc_by_name(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        widget._sort_column = 1
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        assert rows[0][1] == "Bob"
        assert rows[1][1] == "Alice"

    def test_sort_asc_by_id(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][0] == 1
        assert rows[1][0] == 2

    def test_sort_desc_by_id(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        widget._sort_column = 0
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        assert rows[0][0] == 2
        assert rows[1][0] == 1

    def test_none_values_sorted_last_asc(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(
            columns=["val"],
            rows=[(None,), (1,), (3,), (None,), (2,)],
            row_count=5,
        )
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][0] == 1
        assert rows[1][0] == 2
        assert rows[2][0] == 3
        assert rows[3][0] is None
        assert rows[4][0] is None

    def test_none_values_sorted_first_desc(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(
            columns=["val"],
            rows=[(None,), (1,), (3,), (2,)],
            row_count=4,
        )
        widget._sort_column = 0
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        # DESC reverses everything, so (1, "") for None becomes first after reverse
        # but the sort_key puts None with (1, ""), non-None with (0, val)
        # With reverse=True: (1, "") > (0, 3) > (0, 2) > (0, 1)
        # Actually reverse makes (1, "") come first, then (0, 3), (0, 2), (0, 1)
        # So None values come first when DESC due to reverse
        assert rows[0][0] is None
        assert rows[1][0] == 3
        assert rows[2][0] == 2
        assert rows[3][0] == 1

    def test_does_not_mutate_original_rows(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._result = sample_result
        widget._sort_column = 1
        widget._sort_direction = SortDirection.DESC
        original_rows = list(sample_result.rows)
        widget._sorted_rows()
        assert sample_result.rows == original_rows

    def test_mixed_types_fallback_to_string_sort(self, widget: ResultsTable) -> None:
        """Mixed types fall back to string comparison."""
        widget._result = QueryResult(
            columns=["val"],
            rows=[(1,), ("b",), (2,), ("a",)],
            row_count=4,
        )
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows == [(1,), (2,), ("a",), ("b",)]


class TestToggleSort:
    @pytest.fixture
    def sortable_widget(self, sample_result: QueryResult) -> ResultsTable:
        w = ResultsTable()
        w._result = sample_result
        w._table = MagicMock()
        w._table.cursor_column = 0
        w._render_table = MagicMock()  # type: ignore[method-assign]
        return w

    def test_first_toggle_sets_asc(self, sortable_widget: ResultsTable) -> None:
        sortable_widget.action_toggle_sort()
        assert sortable_widget._sort_column == 0
        assert sortable_widget._sort_direction == SortDirection.ASC

    def test_second_toggle_sets_desc(self, sortable_widget: ResultsTable) -> None:
        sortable_widget.action_toggle_sort()
        sortable_widget.action_toggle_sort()
        assert sortable_widget._sort_column == 0
        assert sortable_widget._sort_direction == SortDirection.DESC

    def test_third_toggle_clears_sort(self, sortable_widget: ResultsTable) -> None:
        sortable_widget.action_toggle_sort()
        sortable_widget.action_toggle_sort()
        sortable_widget.action_toggle_sort()
        assert sortable_widget._sort_column is None
        assert sortable_widget._sort_direction == SortDirection.NONE

    def test_switch_column_resets_to_asc(self, sortable_widget: ResultsTable) -> None:
        sortable_widget.action_toggle_sort()  # col 0 ASC
        sortable_widget._table.cursor_column = 1
        sortable_widget.action_toggle_sort()  # col 1 ASC
        assert sortable_widget._sort_column == 1
        assert sortable_widget._sort_direction == SortDirection.ASC

    def test_no_result_does_nothing(self, widget: ResultsTable) -> None:
        widget.action_toggle_sort()
        assert widget._sort_column is None
        assert widget._sort_direction == SortDirection.NONE

    def test_calls_render_table(self, sortable_widget: ResultsTable) -> None:
        sortable_widget.action_toggle_sort()
        sortable_widget._render_table.assert_called_once()  # type: ignore[attr-defined]

    def test_error_result_does_nothing(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(error="some error")
        widget._table = MagicMock()
        widget._table.cursor_column = 0
        widget.action_toggle_sort()
        assert widget._sort_column is None

    def test_no_columns_does_nothing(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(row_count=5)
        widget._table = MagicMock()
        widget._table.cursor_column = 0
        widget.action_toggle_sort()
        assert widget._sort_column is None


class TestSetResultResetsSortState:
    def test_set_result_resets_sort(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._sort_column = 1
        widget._sort_direction = SortDirection.DESC
        widget.set_result(sample_result)
        assert widget._sort_column is None
        assert widget._sort_direction == SortDirection.NONE
