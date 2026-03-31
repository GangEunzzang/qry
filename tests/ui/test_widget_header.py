"""Tests for QryHeader widget."""

from qry.ui.widgets.widget_header import QryHeader


class TestQryHeader:
    def test_is_static_widget(self):
        header = QryHeader()
        assert hasattr(header, "update")

    def test_default_css_height(self):
        assert "height: 1" in QryHeader.DEFAULT_CSS
