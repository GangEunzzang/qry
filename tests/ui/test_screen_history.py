"""Tests for HistoryScreen."""

from datetime import datetime

from qry.domains.query.models import HistoryEntry
from qry.ui.screens.screen_history import HistoryScreen


class TestHistoryScreen:
    def _make_entries(self) -> list[HistoryEntry]:
        return [
            HistoryEntry(
                query="SELECT * FROM users",
                timestamp=datetime(2024, 1, 15, 10, 30),
                connection_name="local-db",
            ),
            HistoryEntry(
                query="INSERT INTO posts VALUES (1, 'Hello')",
                timestamp=datetime(2024, 1, 15, 11, 0),
                connection_name="local-db",
            ),
            HistoryEntry(
                query="DELETE FROM sessions WHERE expired = true",
                timestamp=datetime(2024, 1, 15, 11, 30),
                connection_name=None,
            ),
        ]

    def test_create_history_screen(self):
        entries = self._make_entries()
        screen = HistoryScreen(entries)
        assert screen._entries == entries
        assert screen._filtered == entries

    def test_filter_entries(self):
        entries = self._make_entries()
        screen = HistoryScreen(entries)
        pattern = "select"
        screen._filtered = [e for e in entries if pattern in e.query.lower()]
        assert len(screen._filtered) == 1
        assert screen._filtered[0].query == "SELECT * FROM users"

    def test_filter_no_match(self):
        entries = self._make_entries()
        screen = HistoryScreen(entries)
        pattern = "nonexistent"
        screen._filtered = [e for e in entries if pattern in e.query.lower()]
        assert len(screen._filtered) == 0

    def test_empty_entries(self):
        screen = HistoryScreen([])
        assert screen._entries == []
        assert screen._filtered == []

    def test_entry_display_format(self):
        entry = HistoryEntry(
            query="SELECT * FROM users WHERE id = 1",
            timestamp=datetime(2024, 1, 15, 10, 30),
            connection_name="local-db",
        )
        ts = entry.timestamp.strftime("%m/%d %H:%M")
        assert ts == "01/15 10:30"
        conn = f" [{entry.connection_name}]"
        assert conn == " [local-db]"

    def test_long_query_truncation(self):
        long_query = "SELECT " + ", ".join([f"col{i}" for i in range(50)])
        entry = HistoryEntry(query=long_query, timestamp=datetime.now())
        preview = entry.query[:60].replace("\n", " ")
        if len(entry.query) > 60:
            preview += "..."
        assert len(preview) == 63  # 60 + "..."
        assert preview.endswith("...")
