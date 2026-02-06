"""Database sidebar widget."""

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Static, Tree

from qry.domains.database.base import DatabaseAdapter
from qry.shared.types import TableInfo


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
        self._adapter = adapter
        self.refresh_tree()

    def clear_adapter(self) -> None:
        self._adapter = None
        if self._tree:
            self._tree.clear()

    def refresh_tree(self) -> None:
        if not self._tree or not self._adapter:
            return

        self._tree.clear()
        tables = self._adapter.get_tables()

        tables_node = self._tree.root.add("Tables", expand=True)
        for table in tables:
            tables_node.add_leaf(table.name, data=table)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data and isinstance(event.node.data, TableInfo):
            self.post_message(self.TableSelected(event.node.data.name))

    def toggle(self) -> None:
        self.toggle_class("visible")
