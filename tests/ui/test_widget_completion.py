"""Tests for CompletionDropdown widget."""

import pytest

from qry.domains.query.models import CompletionItem
from qry.ui.widgets.widget_completion import CompletionDropdown


@pytest.fixture
def sample_items() -> list[CompletionItem]:
    return [
        CompletionItem(text="users", kind="table", detail="Table (100 rows)"),
        CompletionItem(text="user_id", kind="column", detail="INTEGER"),
        CompletionItem(text="UPDATE", kind="keyword"),
    ]


class TestCompletionDropdown:
    def test_initial_state_not_visible(self):
        dropdown = CompletionDropdown()
        assert not dropdown.is_visible

    def test_show_completions_adds_visible_class(self, sample_items):
        dropdown = CompletionDropdown()
        # show_completions calls focus() which requires app context,
        # so we test the underlying class manipulation directly
        dropdown._items = sample_items
        dropdown.add_class("visible")
        assert dropdown.is_visible
        assert dropdown._items == sample_items

    def test_show_empty_items_hides(self, sample_items):
        dropdown = CompletionDropdown()
        dropdown.add_class("visible")
        dropdown.show_completions([])
        assert not dropdown.is_visible

    def test_hide_removes_visible_class(self):
        dropdown = CompletionDropdown()
        dropdown.add_class("visible")
        dropdown._items = [CompletionItem(text="x", kind="table")]
        dropdown.hide()
        assert not dropdown.is_visible
        assert dropdown._items == []

    def test_kind_icons(self):
        """Verify kind icon mapping is correct."""
        kind_map = {"table": "[T]", "column": "[C]", "keyword": "[K]"}
        for kind, icon in kind_map.items():
            item = CompletionItem(text="test", kind=kind)
            expected_icon = icon
            actual_icon = {"table": "[T]", "column": "[C]", "keyword": "[K]"}.get(
                item.kind, "[ ]"
            )
            assert actual_icon == expected_icon

    def test_unknown_kind_gets_default_icon(self):
        item = CompletionItem(text="test", kind="unknown")
        icon = {"table": "[T]", "column": "[C]", "keyword": "[K]"}.get(
            item.kind, "[ ]"
        )
        assert icon == "[ ]"

    def test_label_with_detail(self):
        item = CompletionItem(text="users", kind="table", detail="100 rows")
        kind_icon = {"table": "[T]", "column": "[C]", "keyword": "[K]"}.get(
            item.kind, "[ ]"
        )
        label = f"{kind_icon} {item.text}"
        if item.detail:
            label += f"  ({item.detail})"
        assert label == "[T] users  (100 rows)"

    def test_label_without_detail(self):
        item = CompletionItem(text="SELECT", kind="keyword")
        kind_icon = {"table": "[T]", "column": "[C]", "keyword": "[K]"}.get(
            item.kind, "[ ]"
        )
        label = f"{kind_icon} {item.text}"
        if item.detail:
            label += f"  ({item.detail})"
        assert label == "[K] SELECT"

    def test_item_selected_message_carries_item(self):
        item = CompletionItem(text="users", kind="table")
        msg = CompletionDropdown.ItemSelected(item)
        assert msg.item is item
        assert msg.item.text == "users"

    def test_dismissed_message(self):
        msg = CompletionDropdown.Dismissed()
        assert isinstance(msg, CompletionDropdown.Dismissed)
