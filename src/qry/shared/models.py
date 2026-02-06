"""Shared domain models used across multiple domains."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryResult:
    """Result of a database query execution.

    This is a shared model because it's used by:
    - database domain (adapter returns it)
    - query domain (service uses it)
    - export domain (exporters consume it)
    """

    columns: list[str] = field(default_factory=list)
    rows: list[tuple[Any, ...]] = field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: str | None = None
    error_position: int | None = None

    @property
    def is_success(self) -> bool:
        """Check if query executed without errors."""
        return self.error is None

    @property
    def is_empty(self) -> bool:
        """Check if query returned no rows (but succeeded)."""
        return self.row_count == 0 and self.is_success

    def as_dicts(self) -> list[dict[str, Any]]:
        """Convert rows to list of dictionaries."""
        return [dict(zip(self.columns, row)) for row in self.rows]
