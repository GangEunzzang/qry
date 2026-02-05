"""Tests for core types."""

from qry.core.types import ColumnInfo, TableInfo


def test_table_info_creation():
    """Test TableInfo creation."""
    table = TableInfo(name="users", schema="public")
    assert table.name == "users"
    assert table.schema == "public"
    assert table.row_count is None


def test_table_info_frozen():
    """Test TableInfo is immutable."""
    table = TableInfo(name="users")
    try:
        table.name = "other"
        assert False, "Should raise error"
    except AttributeError:
        pass


def test_column_info_creation():
    """Test ColumnInfo creation."""
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
