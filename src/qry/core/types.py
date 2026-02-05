"""Shared data types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableInfo:
    """Information about a database table."""

    name: str
    schema: str | None = None
    row_count: int | None = None


@dataclass(frozen=True)
class ColumnInfo:
    """Information about a table column."""

    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    default: str | None = None
