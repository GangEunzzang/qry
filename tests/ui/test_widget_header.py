"""Tests for QryHeader widget."""

from qry.ui.widgets.widget_header import QryHeader, _LEFT_WIDTH, _RIGHT_WIDTH


class TestQryHeader:
    def test_default_css_height(self):
        assert "height: 1" in QryHeader.DEFAULT_CSS

    def test_left_right_widths_are_positive(self):
        assert _LEFT_WIDTH > 0
        assert _RIGHT_WIDTH > 0

    def test_left_right_widths_fit_80_cols(self):
        assert _LEFT_WIDTH + _RIGHT_WIDTH < 80
