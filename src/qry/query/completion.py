"""SQL autocompletion provider."""

from dataclasses import dataclass

from qry.core.types import ColumnInfo, TableInfo
from qry.database.base import DatabaseAdapter


@dataclass
class CompletionItem:
    """A single completion suggestion."""

    text: str
    kind: str  # "table", "column", "keyword"
    detail: str | None = None


class CompletionProvider:
    """Provides SQL autocompletion suggestions."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        """Initialize completion provider.

        Args:
            adapter: Database adapter for schema information.
        """
        self._adapter = adapter
        self._tables_cache: list[TableInfo] | None = None
        self._columns_cache: dict[str, list[ColumnInfo]] = {}

    def get_completions(self, text: str, cursor_position: int) -> list[CompletionItem]:
        """Get completion suggestions for given text and cursor position.

        Args:
            text: Current SQL text.
            cursor_position: Cursor position in text.

        Returns:
            List of completion suggestions.
        """
        # Get word at cursor
        prefix = self._get_word_at_cursor(text, cursor_position)
        if not prefix:
            return []

        completions: list[CompletionItem] = []

        # Add table completions
        tables = self._get_tables()
        for table in tables:
            if table.name.lower().startswith(prefix.lower()):
                completions.append(
                    CompletionItem(
                        text=table.name,
                        kind="table",
                        detail=f"Table ({table.row_count} rows)" if table.row_count else "Table",
                    )
                )

        # Add column completions based on context
        context_table = self._find_table_context(text, cursor_position)
        if context_table:
            columns = self._get_columns(context_table)
            for col in columns:
                if col.name.lower().startswith(prefix.lower()):
                    completions.append(
                        CompletionItem(
                            text=col.name,
                            kind="column",
                            detail=col.data_type,
                        )
                    )

        return completions

    def _get_word_at_cursor(self, text: str, position: int) -> str:
        """Extract word at cursor position."""
        if position <= 0 or position > len(text):
            return ""

        start = position - 1
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
            start -= 1

        return text[start:position]

    def _find_table_context(self, text: str, position: int) -> str | None:
        """Find table name from context (e.g., after FROM or JOIN)."""
        # Simple heuristic: look for FROM or JOIN followed by table name
        text_before = text[:position].upper()

        for keyword in ["FROM ", "JOIN "]:
            idx = text_before.rfind(keyword)
            if idx != -1:
                after_keyword = text[idx + len(keyword) : position].strip()
                parts = after_keyword.split()
                if parts:
                    return parts[0].strip(",;")

        return None

    def _get_tables(self) -> list[TableInfo]:
        """Get cached tables list."""
        if self._tables_cache is None:
            self._tables_cache = self._adapter.get_tables()
        return self._tables_cache

    def _get_columns(self, table_name: str) -> list[ColumnInfo]:
        """Get cached columns for table."""
        if table_name not in self._columns_cache:
            self._columns_cache[table_name] = self._adapter.get_columns(table_name)
        return self._columns_cache[table_name]

    def invalidate_cache(self) -> None:
        """Clear schema cache."""
        self._tables_cache = None
        self._columns_cache = {}
