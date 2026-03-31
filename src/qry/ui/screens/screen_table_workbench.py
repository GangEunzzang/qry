"""Table Workbench screen — inspect a single table's rows, DDL, indexes, and FKs."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Label, Static, TabbedContent, TabPane

from qry.domains.database.base import DatabaseAdapter
from qry.shared.types import ForeignKeyInfo


class TableWorkbench(ModalScreen[None]):
    """Full-screen workbench for a single table."""

    DEFAULT_CSS = """
    TableWorkbench {
        align: center middle;
    }

    #workbench {
        width: 90%;
        height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #workbench-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #rows-table {
        height: 1fr;
    }

    #ddl-content {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }

    #indexes-table, #fk-table {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
    ]

    def __init__(self, table_name: str, adapter: DatabaseAdapter) -> None:
        super().__init__()
        self._table_name = table_name
        self._adapter = adapter

    def compose(self) -> ComposeResult:
        with Vertical(id="workbench"):
            yield Label(f"// {self._table_name}", id="workbench-title")
            with TabbedContent():
                with TabPane("Rows", id="tab-rows"):
                    yield DataTable(id="rows-table")
                with TabPane("DDL", id="tab-ddl"):
                    yield Static("", id="ddl-content")
                with TabPane("Indexes / FKs", id="tab-indexes"):
                    yield DataTable(id="indexes-table")
                    yield Label("[dim]// foreign keys[/dim]")
                    yield DataTable(id="fk-table")

    def on_mount(self) -> None:
        self._load_rows()
        self._load_ddl()
        self._load_indexes()

    def _load_rows(self) -> None:
        table = self.query_one("#rows-table", DataTable)
        table.cursor_type = "cell"
        safe_name = self._table_name.replace('"', '""')
        result = self._adapter.execute(f'SELECT * FROM "{safe_name}" LIMIT 200')

        if result.error:
            table.add_column("Error")
            table.add_row(f"[!] {result.error}")
            return

        if not result.columns:
            table.add_column("Info")
            table.add_row("No data")
            return

        for col in result.columns:
            table.add_column(col)
        for row in result.rows:
            table.add_row(*[str(v) if v is not None else "NULL" for v in row])

    def _load_ddl(self) -> None:
        ddl_widget = self.query_one("#ddl-content", Static)
        ddl = self._adapter.get_ddl(self._table_name)
        if ddl:
            ddl_widget.update(ddl)
        else:
            ddl_widget.update("[dim]DDL not available for this table.[/dim]")

    def _load_indexes(self) -> None:
        # Indexes
        idx_table = self.query_one("#indexes-table", DataTable)
        idx_table.add_column("Name")
        idx_table.add_column("Table")
        idx_table.add_column("Unique")

        all_indexes = self._adapter.get_indexes()
        table_indexes = [i for i in all_indexes if i.table_name == self._table_name]

        if table_indexes:
            for idx in table_indexes:
                idx_table.add_row(idx.name, idx.table_name, "Yes" if idx.unique else "No")
        else:
            idx_table.add_row("—", "No indexes", "—")

        # Foreign Keys
        fk_table = self.query_one("#fk-table", DataTable)
        fk_table.add_column("From Column")
        fk_table.add_column("To Table")
        fk_table.add_column("To Column")

        fks = self._adapter.get_foreign_keys(self._table_name)
        if fks:
            for fk in fks:
                fk_table.add_row(fk.from_column, fk.to_table, fk.to_column)
        else:
            fk_table.add_row("—", "No foreign keys", "—")

    def action_dismiss(self) -> None:
        self.dismiss(None)
