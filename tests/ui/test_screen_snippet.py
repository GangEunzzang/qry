"""Tests for SnippetScreen."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from qry.domains.snippet.models import Snippet
from qry.ui.screens.screen_snippet import SnippetScreen


class TestSnippetScreen:
    def _make_snippets(self) -> list[Snippet]:
        return [
            Snippet(
                name="select_users",
                query="SELECT * FROM users",
                description="Get all users",
                category="queries",
                created_at=datetime(2024, 1, 1),
            ),
            Snippet(
                name="insert_post",
                query="INSERT INTO posts (title) VALUES ('test')",
                description="Create a test post",
                category="mutations",
                created_at=datetime(2024, 1, 2),
            ),
            Snippet(
                name="count_orders",
                query="SELECT COUNT(*) FROM orders",
                description="Count all orders",
                category="queries",
                created_at=datetime(2024, 1, 3),
            ),
        ]

    def test_create_snippet_screen(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        assert screen._snippets == snippets
        assert screen._filtered == snippets

    @patch.object(SnippetScreen, "_refresh_list")
    def test_filter_by_name(self, _mock_refresh):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        event = MagicMock()
        event.value = "select"
        screen.on_input_changed(event)
        assert len(screen._filtered) == 2  # select_users and count_orders (has SELECT in query)

    @patch.object(SnippetScreen, "_refresh_list")
    def test_filter_by_description(self, _mock_refresh):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        event = MagicMock()
        event.value = "test post"
        screen.on_input_changed(event)
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "insert_post"

    @patch.object(SnippetScreen, "_refresh_list")
    def test_filter_by_category(self, _mock_refresh):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        event = MagicMock()
        event.value = "mutations"
        screen.on_input_changed(event)
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "insert_post"

    @patch.object(SnippetScreen, "_refresh_list")
    def test_filter_by_query_content(self, _mock_refresh):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        event = MagicMock()
        event.value = "count(*)"
        screen.on_input_changed(event)
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "count_orders"

    @patch.object(SnippetScreen, "_refresh_list")
    def test_filter_no_match(self, _mock_refresh):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        event = MagicMock()
        event.value = "nonexistent"
        screen.on_input_changed(event)
        assert len(screen._filtered) == 0

    def test_empty_snippets(self):
        screen = SnippetScreen([])
        assert screen._snippets == []
        assert screen._filtered == []

    def test_label_format_with_category_and_description(self):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            description="A test snippet",
            category="dev",
        )
        label = SnippetScreen._format_snippet_label(snippet)
        assert label == "[dev] test - A test snippet"

    def test_label_format_without_category(self):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            description="A test snippet",
        )
        label = SnippetScreen._format_snippet_label(snippet)
        assert label == "test - A test snippet"

    def test_label_format_without_description(self):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            category="dev",
        )
        label = SnippetScreen._format_snippet_label(snippet)
        assert label == "[dev] test"

    def test_label_format_minimal(self):
        snippet = Snippet(name="test", query="SELECT 1")
        label = SnippetScreen._format_snippet_label(snippet)
        assert label == "test"
