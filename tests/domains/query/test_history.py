"""Tests for HistoryManager."""

from pathlib import Path

import pytest

from qry.domains.query.history import HistoryManager


class TestHistoryManager:
    @pytest.fixture
    def history(self, tmp_config_dir: Path) -> HistoryManager:
        return HistoryManager()

    def test_initially_empty(self, history: HistoryManager):
        entries = history.get_recent()

        assert entries == []

    def test_add_entry(self, history: HistoryManager):
        history.add("SELECT * FROM users")

        entries = history.get_recent()

        assert len(entries) == 1
        assert entries[0].query == "SELECT * FROM users"

    def test_add_strips_whitespace(self, history: HistoryManager):
        history.add("  SELECT 1  ")

        entries = history.get_recent()

        assert entries[0].query == "SELECT 1"

    def test_get_recent_returns_newest_first(self, history: HistoryManager):
        history.add("SELECT 1")
        history.add("SELECT 2")
        history.add("SELECT 3")

        entries = history.get_recent()

        assert entries[0].query == "SELECT 3"
        assert entries[1].query == "SELECT 2"
        assert entries[2].query == "SELECT 1"

    def test_get_recent_limit(self, history: HistoryManager):
        for i in range(10):
            history.add(f"SELECT {i}")

        entries = history.get_recent(count=3)

        assert len(entries) == 3
        assert entries[0].query == "SELECT 9"

    def test_search(self, history: HistoryManager):
        history.add("SELECT * FROM users")
        history.add("SELECT * FROM posts")
        history.add("INSERT INTO users VALUES (1)")

        results = history.search("users")

        assert len(results) == 2
        queries = [r.query for r in results]
        assert "SELECT * FROM users" in queries
        assert "INSERT INTO users VALUES (1)" in queries

    def test_search_case_insensitive(self, history: HistoryManager):
        history.add("SELECT * FROM USERS")
        history.add("select * from users")

        results = history.search("users")

        assert len(results) == 2

    def test_clear(self, history: HistoryManager):
        history.add("SELECT 1")
        history.add("SELECT 2")

        history.clear()

        assert history.get_recent() == []

    def test_max_entries(self, tmp_config_dir: Path):
        history = HistoryManager(max_entries=5)

        for i in range(10):
            history.add(f"SELECT {i}")

        entries = history.get_recent()

        assert len(entries) == 5
        # Should have the 5 most recent
        assert entries[0].query == "SELECT 9"
        assert entries[-1].query == "SELECT 5"

    def test_set_connection(self, history: HistoryManager):
        history.set_connection("test_db")
        history.add("SELECT 1")

        entries = history.get_recent()

        assert entries[0].connection_name == "test_db"

    def test_persistence(self, tmp_config_dir: Path):
        history1 = HistoryManager()
        history1.add("SELECT persistent")
        history1.save()

        history2 = HistoryManager()
        entries = history2.get_recent()

        assert len(entries) == 1
        assert entries[0].query == "SELECT persistent"
