"""Query domain models."""

from dataclasses import dataclass
from datetime import datetime

# Re-export QueryResult from shared for backward compatibility
from qry.shared.models import QueryResult

__all__ = ["QueryResult", "HistoryEntry", "CompletionItem"]


@dataclass
class HistoryEntry:
    query: str
    timestamp: datetime
    connection_name: str | None = None


@dataclass
class CompletionItem:
    text: str
    kind: str  # "table", "column", "keyword"
    detail: str | None = None
