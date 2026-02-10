"""Tests for ResultsTable clipboard copy, column sorting, and search."""

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


def _init_widget(widget: ResultsTable, result: QueryResult) -> None:
    """Set result and _all_rows on widget without requiring mounted DataTable."""
    widget._result = result
    widget._all_rows = list(result.rows) if result.rows else []


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
            rows=[("\ud55c\uae00 \ud14c\uc2a4\ud2b8",)],
            row_count=1,
        )
        result = widget._get_row_as_json(0)
        assert result is not None
        assert "\ud55c\uae00 \ud14c\uc2a4\ud2b8" in result


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
        _init_widget(widget, sample_result)
        rows = widget._sorted_rows()
        assert rows == list(sample_result.rows)

    def test_sort_asc_by_name(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._sort_column = 1
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][1] == "Alice"
        assert rows[1][1] == "Bob"

    def test_sort_desc_by_name(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._sort_column = 1
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        assert rows[0][1] == "Bob"
        assert rows[1][1] == "Alice"

    def test_sort_asc_by_id(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][0] == 1
        assert rows[1][0] == 2

    def test_sort_desc_by_id(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._sort_column = 0
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        assert rows[0][0] == 2
        assert rows[1][0] == 1

    def test_none_values_sorted_last_asc(self, widget: ResultsTable) -> None:
        result = QueryResult(
            columns=["val"],
            rows=[(None,), (1,), (3,), (None,), (2,)],
            row_count=5,
        )
        _init_widget(widget, result)
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows[0][0] == 1
        assert rows[1][0] == 2
        assert rows[2][0] == 3
        assert rows[3][0] is None
        assert rows[4][0] is None

    def test_none_values_sorted_first_desc(self, widget: ResultsTable) -> None:
        result = QueryResult(
            columns=["val"],
            rows=[(None,), (1,), (3,), (2,)],
            row_count=4,
        )
        _init_widget(widget, result)
        widget._sort_column = 0
        widget._sort_direction = SortDirection.DESC
        rows = widget._sorted_rows()
        assert rows[0][0] is None
        assert rows[1][0] == 3
        assert rows[2][0] == 2
        assert rows[3][0] == 1

    def test_does_not_mutate_original_rows(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._sort_column = 1
        widget._sort_direction = SortDirection.DESC
        original_rows = list(sample_result.rows)
        widget._sorted_rows()
        assert sample_result.rows == original_rows

    def test_mixed_types_fallback_to_string_sort(self, widget: ResultsTable) -> None:
        """Mixed types fall back to string comparison."""
        result = QueryResult(
            columns=["val"],
            rows=[(1,), ("b",), (2,), ("a",)],
            row_count=4,
        )
        _init_widget(widget, result)
        widget._sort_column = 0
        widget._sort_direction = SortDirection.ASC
        rows = widget._sorted_rows()
        assert rows == [(1,), (2,), ("a",), ("b",)]


class TestToggleSort:
    @pytest.fixture
    def sortable_widget(self, sample_result: QueryResult) -> ResultsTable:
        w = ResultsTable()
        w._result = sample_result
        w._all_rows = list(sample_result.rows)
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

    def test_set_result_resets_search(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget._search_active = True
        widget._search_query = "alice"
        widget.set_result(sample_result)
        assert widget._search_active is False
        assert widget._search_query == ""

    def test_set_result_stores_all_rows(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        widget.set_result(sample_result)
        assert widget._all_rows == list(sample_result.rows)


class TestFilterRows:
    def test_no_query_returns_all(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert filtered == rows

    def test_filter_by_name(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = "alice"
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert len(filtered) == 1
        assert filtered[0][1] == "Alice"

    def test_filter_case_insensitive(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = "ALICE"
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert len(filtered) == 1
        assert filtered[0][1] == "Alice"

    def test_filter_matches_any_column(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = "example.com"
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert len(filtered) == 1
        assert filtered[0][1] == "Alice"

    def test_filter_no_match(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = "nonexistent"
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert len(filtered) == 0

    def test_filter_matches_numeric_value(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = "1"
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert len(filtered) == 1
        assert filtered[0][0] == 1

    def test_filter_matches_null_value(self, widget: ResultsTable) -> None:
        result = QueryResult(
            columns=["name", "value"],
            rows=[("a", None), ("b", "something")],
            row_count=2,
        )
        _init_widget(widget, result)
        widget._search_query = "null"
        filtered = widget._filter_rows(list(result.rows))
        assert len(filtered) == 1
        assert filtered[0][0] == "a"

    def test_filter_empty_query_returns_all(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_query = ""
        rows = list(sample_result.rows)
        filtered = widget._filter_rows(rows)
        assert filtered == rows

    def test_filter_partial_match(self, widget: ResultsTable) -> None:
        result = QueryResult(
            columns=["name"],
            rows=[("foobar",), ("bazqux",), ("fooqux",)],
            row_count=3,
        )
        _init_widget(widget, result)
        widget._search_query = "foo"
        filtered = widget._filter_rows(list(result.rows))
        assert len(filtered) == 2
        assert filtered[0][0] == "foobar"
        assert filtered[1][0] == "fooqux"


class TestSearchState:
    def test_initial_search_state(self, widget: ResultsTable) -> None:
        assert widget._search_active is False
        assert widget._search_query == ""
        assert widget._all_rows == []

    def test_close_search_with_keep_filter(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._table = MagicMock()
        widget._render_table = MagicMock()  # type: ignore[method-assign]
        widget._search_active = True
        widget._search_query = "alice"
        widget._close_search(keep_filter=True)
        assert widget._search_active is False
        assert widget._search_query == "alice"

    def test_close_search_without_keep_filter(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._table = MagicMock()
        widget._render_table = MagicMock()  # type: ignore[method-assign]
        widget._search_active = True
        widget._search_query = "alice"
        widget._close_search(keep_filter=False)
        assert widget._search_active is False
        assert widget._search_query == ""

    def test_start_search_no_result(self, widget: ResultsTable) -> None:
        widget.action_start_search()
        assert widget._search_active is False

    def test_start_search_no_columns(self, widget: ResultsTable) -> None:
        widget._result = QueryResult(row_count=5)
        widget.action_start_search()
        assert widget._search_active is False

    def test_start_search_with_result(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget.action_start_search()
        assert widget._search_active is True

    def test_escape_clears_search(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._table = MagicMock()
        widget._render_table = MagicMock()  # type: ignore[method-assign]
        widget._search_active = True
        widget._search_query = "alice"
        widget.key_escape()
        assert widget._search_active is False
        assert widget._search_query == ""

    def test_escape_noop_when_not_searching(self, widget: ResultsTable) -> None:
        widget.key_escape()
        assert widget._search_active is False
        assert widget._search_query == ""


class TestUpdateBorderTitle:
    def test_normal_title(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        rows = list(sample_result.rows)
        widget._update_border_title(rows)
        assert "2 rows" in widget.border_title
        assert "1.5ms" in widget.border_title

    def test_filtered_title(
        self, widget: ResultsTable, sample_result: QueryResult
    ) -> None:
        _init_widget(widget, sample_result)
        widget._search_active = True
        widget._search_query = "alice"
        filtered = [sample_result.rows[0]]
        widget._update_border_title(filtered)
        assert "1/2 rows (filtered)" in widget.border_title

    def test_no_result_noop(self, widget: ResultsTable) -> None:
        widget._update_border_title([])
