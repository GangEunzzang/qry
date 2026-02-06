"""Tests for shared types."""

import pytest

from qry.shared.types import ColumnInfo, TableInfo


class TestTableInfo:
    def test_creation(self):
        table = TableInfo(name="users", schema="public")

        assert table.name == "users"
        assert table.schema == "public"
        assert table.row_count is None

    def test_creation_with_row_count(self):
        table = TableInfo(name="users", row_count=100)

        assert table.name == "users"
        assert table.row_count == 100

    def test_frozen(self):
        table = TableInfo(name="users")

        with pytest.raises(AttributeError):
            table.name = "other"

    def test_equality(self):
        t1 = TableInfo(name="users", schema="public")
        t2 = TableInfo(name="users", schema="public")

        assert t1 == t2


class TestColumnInfo:
    def test_creation(self):
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
        assert col.default is None

    def test_defaults(self):
        col = ColumnInfo(name="name", data_type="TEXT")

        assert col.nullable is True
        assert col.primary_key is False
        assert col.default is None

    def test_frozen(self):
        col = ColumnInfo(name="id", data_type="INTEGER")

        with pytest.raises(AttributeError):
            col.name = "other"
