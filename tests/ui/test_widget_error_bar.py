"""Tests for ErrorBar widget."""

from qry.ui.widgets.widget_error_bar import ErrorBar


def _get_content(bar: ErrorBar) -> str:
    """Get the text content of an ErrorBar."""
    return str(bar._Static__content)


class TestErrorBar:
    def test_initial_state_hidden(self):
        bar = ErrorBar()
        assert not bar.has_class("visible")

    def test_show_error_adds_visible_class(self):
        bar = ErrorBar()
        bar.show_error("syntax error")
        assert bar.has_class("visible")

    def test_show_error_with_position_includes_line(self):
        bar = ErrorBar()
        bar.show_error("unexpected token", position=5)
        assert bar.has_class("visible")
        assert _get_content(bar) == "\u2717 [Line 5] unexpected token"

    def test_show_error_without_position_no_line_prefix(self):
        bar = ErrorBar()
        bar.show_error("connection failed")
        assert _get_content(bar) == "\u2717 connection failed"

    def test_clear_error_removes_visible_class(self):
        bar = ErrorBar()
        bar.show_error("some error")
        bar.clear_error()
        assert not bar.has_class("visible")
        assert _get_content(bar) == ""
