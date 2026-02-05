"""Tests for core types."""

import pytest

from qry.core.core_types import ColumnInfo, TableInfo


def test_table_info_creation():
    table = TableInfo(name="users", schema="public")
    assert table.name == "users"
    assert table.schema == "public"
    assert table.row_count is None


def test_table_info_frozen():
    table = TableInfo(name="users")
    with pytest.raises(AttributeError):
        table.name = "other"


def test_column_info_creation():
    col = ColumnInfo(
        name="id",
        data_type="INTEGER",
        nullable=False,
        primary_key=True,
    )
    assert col.name == "id"
    assert col.data_type == "INTEGER"
    assert col.nullable is False
    assert col.primary_key is True
