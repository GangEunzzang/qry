"""Shared data types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableInfo:
    name: str
    schema: str | None = None
    row_count: int | None = None


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    default: str | None = None


@dataclass(frozen=True)
class ViewInfo:
    name: str
    schema: str | None = None


@dataclass(frozen=True)
class IndexInfo:
    name: str
    table_name: str
    unique: bool = False
    schema: str | None = None
