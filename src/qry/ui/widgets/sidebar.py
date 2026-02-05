"""Database sidebar widget."""

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Static, Tree

from qry.core.types import TableInfo
from qry.database.base import DatabaseAdapter


class DatabaseSidebar(Static):
    """Sidebar showing database structure."""

    DEFAULT_CSS = """
    DatabaseSidebar {
        width: 30;
        border: solid $primary;
        display: none;
    }

    DatabaseSidebar.visible {
        display: block;
    }

    DatabaseSidebar Tree {
        height: 100%;
    }
    """

    class TableSelected(Message):
        """Table was selected."""

        def __init__(self, table_name: str) -> None:
            super().__init__()
            self.table_name = table_name

    def __init__(self, id: str | None = None) -> None:
        super().__init__(id=id)
        self._adapter: DatabaseAdapter | None = None
        self._tree: Tree | None = None

    def compose(self) -> ComposeResult:
        yield Tree("Database", id="db-tree")

    def on_mount(self) -> None:
        self._tree = self.query_one("#db-tree", Tree)
        self._tree.root.expand()
        self.border_title = "Tables"

    def set_adapter(self, adapter: DatabaseAdapter) -> None:
        """Set database adapter and refresh tree.

        Args:
            adapter: Database adapter.
        """
        self._adapter = adapter
        self.refresh_tree()

    def refresh_tree(self) -> None:
        """Refresh the database tree."""
        if not self._tree or not self._adapter:
            return

        self._tree.clear()
        tables = self._adapter.get_tables()

        tables_node = self._tree.root.add("Tables", expand=True)
        for table in tables:
            tables_node.add_leaf(table.name, data=table)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection."""
        if event.node.data and isinstance(event.node.data, TableInfo):
            self.post_message(self.TableSelected(event.node.data.name))

    def toggle(self) -> None:
        """Toggle sidebar visibility."""
        self.toggle_class("visible")
