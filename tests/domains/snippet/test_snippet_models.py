"""Tests for Snippet models."""

from datetime import UTC, datetime

from qry.domains.snippet.snippet_models import Snippet


class TestSnippet:
    def test_create_snippet(self):
        snippet = Snippet(
            name="select_users",
            query="SELECT * FROM users",
            description="Get all users",
            category="queries",
        )
        assert snippet.name == "select_users"
        assert snippet.query == "SELECT * FROM users"
        assert snippet.description == "Get all users"
        assert snippet.category == "queries"
        assert isinstance(snippet.created_at, datetime)

    def test_create_snippet_minimal(self):
        snippet = Snippet(name="test", query="SELECT 1")
        assert snippet.name == "test"
        assert snippet.query == "SELECT 1"
        assert snippet.description == ""
        assert snippet.category == ""

    def test_created_at_default(self):
        before = datetime.now(UTC)
        snippet = Snippet(name="test", query="SELECT 1")
        after = datetime.now(UTC)
        assert before <= snippet.created_at <= after

    def test_created_at_explicit(self):
        ts = datetime(2024, 6, 15, 12, 0, 0)
        snippet = Snippet(name="test", query="SELECT 1", created_at=ts)
        assert snippet.created_at == ts

    def test_snippet_equality(self):
        ts = datetime(2024, 1, 1)
        s1 = Snippet(name="a", query="SELECT 1", created_at=ts)
        s2 = Snippet(name="a", query="SELECT 1", created_at=ts)
        assert s1 == s2

    def test_snippet_inequality(self):
        ts = datetime(2024, 1, 1)
        s1 = Snippet(name="a", query="SELECT 1", created_at=ts)
        s2 = Snippet(name="b", query="SELECT 1", created_at=ts)
        assert s1 != s2
