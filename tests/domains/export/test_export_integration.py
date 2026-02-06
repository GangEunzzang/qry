"""Tests for CSV and JSON exporters."""

import json
from pathlib import Path

import pytest

from qry.domains.export.csv import CsvExporter
from qry.domains.export.json import JsonExporter
from qry.shared.models import QueryResult


@pytest.fixture
def sample_result():
    return QueryResult(
        columns=["id", "name", "email"],
        rows=[
            (1, "Alice", "alice@example.com"),
            (2, "Bob", "bob@example.com"),
        ],
        row_count=2,
        execution_time_ms=10.5,
    )


@pytest.fixture
def empty_result():
    return QueryResult(columns=["id"], rows=[], row_count=0, execution_time_ms=1.0)


class TestCsvExporter:

    def test_export_creates_file(self, tmp_path: Path, sample_result: QueryResult):
        path = tmp_path / "output.csv"
        CsvExporter().export(sample_result, path)
        assert path.exists()

    def test_export_content(self, tmp_path: Path, sample_result: QueryResult):
        path = tmp_path / "output.csv"
        CsvExporter().export(sample_result, path)
        content = path.read_text()
        assert "id,name,email" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_export_string(self, sample_result: QueryResult):
        result = CsvExporter().export_string(sample_result)
        lines = result.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows

    def test_export_empty_result(self, tmp_path: Path, empty_result: QueryResult):
        path = tmp_path / "output.csv"
        CsvExporter().export(empty_result, path)
        content = path.read_text()
        assert "id" in content


class TestJsonExporter:

    def test_export_creates_file(self, tmp_path: Path, sample_result: QueryResult):
        path = tmp_path / "output.json"
        JsonExporter().export(sample_result, path)
        assert path.exists()

    def test_export_content(self, tmp_path: Path, sample_result: QueryResult):
        path = tmp_path / "output.json"
        JsonExporter().export(sample_result, path)
        data = json.loads(path.read_text())
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["email"] == "bob@example.com"

    def test_export_string(self, sample_result: QueryResult):
        result = JsonExporter().export_string(sample_result)
        data = json.loads(result)
        assert len(data) == 2

    def test_export_empty_result(self, tmp_path: Path, empty_result: QueryResult):
        path = tmp_path / "output.json"
        JsonExporter().export(empty_result, path)
        data = json.loads(path.read_text())
        assert data == []

    def test_export_preserves_types(self, tmp_path: Path):
        result = QueryResult(
            columns=["id", "value", "flag"],
            rows=[(1, 3.14, True)],
            row_count=1,
        )
        path = tmp_path / "output.json"
        JsonExporter().export(result, path)
        data = json.loads(path.read_text())
        assert data[0]["id"] == 1
        assert data[0]["value"] == 3.14
        assert data[0]["flag"] is True
