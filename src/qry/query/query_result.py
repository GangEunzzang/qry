"""Query result data class."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[tuple[Any, ...]] = field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    error: str | None = None
    error_position: int | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_empty(self) -> bool:
        return self.row_count == 0 and self.is_success
