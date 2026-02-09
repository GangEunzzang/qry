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
        height: 100%;
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
        self._columns_loaded: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Tree("Database", id="db-tree")

    def set_adapter(self, adapter: DatabaseAdapter) -> None:
        self._adapter = adapter
        self._columns_loaded.clear()
        if self._tree:
            self.refresh_tree()

    def on_mount(self) -> None:
        self._tree = self.query_one("#db-tree", Tree)
        self._tree.root.expand()
        self.border_title = "Database"
        if self._adapter:
            self.refresh_tree()

    def clear_adapter(self) -> None:
        self._adapter = None
        self._columns_loaded.clear()
        if self._tree:
            self._tree.clear()

    def refresh_tree(self) -> None:
        if not self._tree or not self._adapter:
            return

        self._tree.clear()
        self._columns_loaded.clear()

        # Tables
        tables = self._adapter.get_tables()
        tables_node = self._tree.root.add(f"Tables ({len(tables)})", expand=True)
        for table in tables:
            table_node = tables_node.add(table.name, data=table, expand=False)
            table_node.allow_expand = True

        # Views
        views = self._adapter.get_views()
        if views:
            views_node = self._tree.root.add(f"Views ({len(views)})", expand=False)
            for view in views:
                views_node.add_leaf(view.name, data=view)

        # Indexes
        indexes = self._adapter.get_indexes()
        if indexes:
            indexes_node = self._tree.root.add(f"Indexes ({len(indexes)})", expand=False)
            for idx in indexes:
                label = f"{idx.name} → {idx.table_name}"
                if idx.unique:
                    label = f"⚷ {label}"
                indexes_node.add_leaf(label)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Lazy-load columns when a table node is expanded."""
        node = event.node
        if not isinstance(node.data, TableInfo) or not self._adapter:
            return

        table_name = node.data.name
        if table_name in self._columns_loaded:
            return

        self._columns_loaded.add(table_name)
        columns = self._adapter.get_columns(table_name)
        for col in columns:
            prefix = "🔑 " if col.primary_key else ""
            type_str = col.data_type
            if col.length is not None:
                type_str = f"{col.data_type}({col.length})"
            label = f"{prefix}{col.name} ({type_str})"
            node.add_leaf(label)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data and isinstance(event.node.data, TableInfo):
            self.post_message(self.TableSelected(event.node.data.name))

    def toggle(self) -> None:
        self.toggle_class("visible")
