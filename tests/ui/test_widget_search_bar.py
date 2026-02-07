"""Tests for ReverseSearchBar widget."""

from datetime import datetime

from qry.domains.query.models import HistoryEntry
from qry.ui.widgets.widget_search_bar import ReverseSearchBar


def _make_entries(queries: list[str]) -> list[HistoryEntry]:
    """Create HistoryEntry objects from query strings."""
    return [HistoryEntry(query=q, timestamp=datetime.now()) for q in queries]


def _make_search_callback(
    entries: list[HistoryEntry],
) -> callable:
    """Create a search callback that filters entries by pattern."""

    def callback(pattern: str, limit: int) -> list[HistoryEntry]:
        pattern_lower = pattern.lower()
        results = [e for e in entries if pattern_lower in e.query.lower()]
        return results[:limit]

    return callback


class TestReverseSearchBar:
    def test_initial_state_hidden(self):
        bar = ReverseSearchBar()
        assert not bar.is_visible

    def test_open_adds_visible_class(self):
        bar = ReverseSearchBar()
        bar._input = None  # Skip focus attempt
        bar.add_class("visible")
        assert bar.is_visible

    def test_close_removes_visible_class(self):
        bar = ReverseSearchBar()
        bar.add_class("visible")
        bar.close()
        assert not bar.is_visible

    def test_close_resets_matches(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1"])
        bar._match_index = 0
        bar.close()
        assert bar._matches == []
        assert bar._match_index == 0

    def test_current_match_returns_none_when_no_matches(self):
        bar = ReverseSearchBar()
        assert bar.current_match is None

    def test_current_match_returns_query(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1", "SELECT 2"])
        bar._match_index = 0
        assert bar.current_match == "SELECT 1"

    def test_current_match_at_different_index(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1", "SELECT 2"])
        bar._match_index = 1
        assert bar.current_match == "SELECT 2"

    def test_do_search_with_callback(self):
        bar = ReverseSearchBar()
        entries = _make_entries(
            ["SELECT * FROM users", "SELECT 1", "INSERT INTO users"]
        )
        bar._search_callback = _make_search_callback(entries)

        bar._do_search("users")

        assert len(bar._matches) == 2
        assert bar._match_index == 0

    def test_do_search_empty_pattern_clears_matches(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1"])
        bar._search_callback = _make_search_callback([])

        bar._do_search("")

        assert bar._matches == []
        assert bar._match_index == 0

    def test_do_search_no_callback_clears_matches(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1"])

        bar._do_search("test")

        assert bar._matches == []

    def test_action_next_match_cycles(self):
        bar = ReverseSearchBar()
        bar._matches = _make_entries(["SELECT 1", "SELECT 2", "SELECT 3"])
        bar._match_index = 0
        bar._preview = None  # Skip preview update

        bar.action_next_match()
        assert bar._match_index == 1

        bar.action_next_match()
        assert bar._match_index == 2

        bar.action_next_match()
        assert bar._match_index == 0  # wraps around

    def test_action_next_match_no_matches_does_nothing(self):
        bar = ReverseSearchBar()
        bar._matches = []
        bar._match_index = 0

        bar.action_next_match()  # should not raise
        assert bar._match_index == 0

    def test_accepted_message_carries_query(self):
        msg = ReverseSearchBar.Accepted("SELECT * FROM users")
        assert msg.query == "SELECT * FROM users"

    def test_cancelled_message(self):
        msg = ReverseSearchBar.Cancelled()
        assert isinstance(msg, ReverseSearchBar.Cancelled)

    def test_do_search_case_insensitive(self):
        bar = ReverseSearchBar()
        entries = _make_entries(["SELECT * FROM USERS", "select * from users"])
        bar._search_callback = _make_search_callback(entries)

        bar._do_search("users")

        assert len(bar._matches) == 2

    def test_do_search_respects_limit(self):
        bar = ReverseSearchBar()
        entries = _make_entries([f"SELECT {i} FROM users" for i in range(100)])

        def limited_callback(pattern: str, limit: int) -> list[HistoryEntry]:
            return _make_search_callback(entries)(pattern, limit)

        bar._search_callback = limited_callback
        bar._do_search("users")

        assert len(bar._matches) <= 50
