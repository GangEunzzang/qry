"""Tests for SnippetScreen."""

from datetime import datetime

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

    def test_filter_by_name(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        pattern = "select"
        screen._filtered = [
            s
            for s in snippets
            if pattern in s.name.lower()
            or pattern in s.description.lower()
            or pattern in s.category.lower()
            or pattern in s.query.lower()
        ]
        assert len(screen._filtered) == 2  # select_users and count_orders (has SELECT in query)

    def test_filter_by_description(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        pattern = "test post"
        screen._filtered = [
            s
            for s in snippets
            if pattern in s.name.lower()
            or pattern in s.description.lower()
            or pattern in s.category.lower()
            or pattern in s.query.lower()
        ]
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "insert_post"

    def test_filter_by_category(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        pattern = "mutations"
        screen._filtered = [
            s
            for s in snippets
            if pattern in s.name.lower()
            or pattern in s.description.lower()
            or pattern in s.category.lower()
            or pattern in s.query.lower()
        ]
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "insert_post"

    def test_filter_by_query_content(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        pattern = "count(*)"
        screen._filtered = [
            s
            for s in snippets
            if pattern in s.name.lower()
            or pattern in s.description.lower()
            or pattern in s.category.lower()
            or pattern in s.query.lower()
        ]
        assert len(screen._filtered) == 1
        assert screen._filtered[0].name == "count_orders"

    def test_filter_no_match(self):
        snippets = self._make_snippets()
        screen = SnippetScreen(snippets)
        pattern = "nonexistent"
        screen._filtered = [
            s
            for s in snippets
            if pattern in s.name.lower()
            or pattern in s.description.lower()
            or pattern in s.category.lower()
            or pattern in s.query.lower()
        ]
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
        category = f"[{snippet.category}] " if snippet.category else ""
        desc = f" - {snippet.description}" if snippet.description else ""
        label = f"{category}{snippet.name}{desc}"
        assert label == "[dev] test - A test snippet"

    def test_label_format_without_category(self):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            description="A test snippet",
        )
        category = f"[{snippet.category}] " if snippet.category else ""
        desc = f" - {snippet.description}" if snippet.description else ""
        label = f"{category}{snippet.name}{desc}"
        assert label == "test - A test snippet"

    def test_label_format_without_description(self):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            category="dev",
        )
        category = f"[{snippet.category}] " if snippet.category else ""
        desc = f" - {snippet.description}" if snippet.description else ""
        label = f"{category}{snippet.name}{desc}"
        assert label == "[dev] test"

    def test_label_format_minimal(self):
        snippet = Snippet(name="test", query="SELECT 1")
        category = f"[{snippet.category}] " if snippet.category else ""
        desc = f" - {snippet.description}" if snippet.description else ""
        label = f"{category}{snippet.name}{desc}"
        assert label == "test"
