"""SQL autocompletion provider."""

from qry.domains.query.models import CompletionItem
from qry.domains.query.ports import SchemaProvider
from qry.shared.constants import SQL_TABLE_CONTEXT_KEYWORDS
from qry.shared.types import ColumnInfo, TableInfo


class CompletionProvider:
    """Provides SQL autocompletion suggestions.

    Uses SchemaProvider port to access database schema, keeping
    this domain independent of the database domain.
    """

    def __init__(self, schema_provider: SchemaProvider) -> None:
        self._schema = schema_provider
        self._tables_cache: list[TableInfo] | None = None
        self._columns_cache: dict[str, list[ColumnInfo]] = {}

    def get_completions(self, text: str, cursor_position: int) -> list[CompletionItem]:
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
        if position <= 0 or position > len(text):
            return ""

        start = position - 1
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] == "_"):
            start -= 1

        return text[start:position]

    def _find_table_context(self, text: str, position: int) -> str | None:
        text_before = text[:position].upper()

        for keyword in SQL_TABLE_CONTEXT_KEYWORDS:
            idx = text_before.rfind(keyword)
            if idx != -1:
                after_keyword = text[idx + len(keyword) : position].strip()
                parts = after_keyword.split()
                if parts:
                    return parts[0].strip(",;")

        return None

    def _get_tables(self) -> list[TableInfo]:
        if self._tables_cache is None:
            self._tables_cache = self._schema.get_tables()
        return self._tables_cache

    def _get_columns(self, table_name: str) -> list[ColumnInfo]:
        if table_name not in self._columns_cache:
            self._columns_cache[table_name] = self._schema.get_columns(table_name)
        return self._columns_cache[table_name]

    def invalidate_cache(self) -> None:
        self._tables_cache = None
        self._columns_cache = {}
