"""Tests for exporters."""

import json
from pathlib import Path

import pytest

from qry.domains.export.csv import CsvExporter
from qry.domains.export.json import JsonExporter
from qry.domains.query.models import QueryResult


class TestCsvExporter:
    @pytest.fixture
    def exporter(self) -> CsvExporter:
        return CsvExporter()

    @pytest.fixture
    def sample_result(self) -> QueryResult:
        return QueryResult(
            columns=["id", "name", "email"],
            rows=[
                (1, "Alice", "alice@example.com"),
                (2, "Bob", "bob@example.com"),
            ],
            row_count=2,
        )

    def test_export_string(self, exporter: CsvExporter, sample_result: QueryResult):
        output = exporter.export_string(sample_result)

        # Normalize line endings for cross-platform compatibility
        lines = output.strip().replace("\r\n", "\n").split("\n")
        assert len(lines) == 3
        assert lines[0] == "id,name,email"
        assert lines[1] == "1,Alice,alice@example.com"
        assert lines[2] == "2,Bob,bob@example.com"

    def test_export_to_file(
        self, exporter: CsvExporter, sample_result: QueryResult, tmp_path: Path
    ):
        output_path = tmp_path / "output.csv"

        exporter.export(sample_result, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "id,name,email" in content
        assert "Alice" in content

    def test_export_empty_result(self, exporter: CsvExporter):
        result = QueryResult(columns=["id"], rows=[], row_count=0)

        output = exporter.export_string(result)

        assert output.strip() == "id"

    def test_export_with_special_chars(self, exporter: CsvExporter):
        result = QueryResult(
            columns=["text"],
            rows=[('Hello, "World"',), ("Line1\nLine2",)],
            row_count=2,
        )

        output = exporter.export_string(result)

        # CSV should properly escape quotes and newlines
        assert "Hello" in output


class TestJsonExporter:
    @pytest.fixture
    def exporter(self) -> JsonExporter:
        return JsonExporter()

    @pytest.fixture
    def sample_result(self) -> QueryResult:
        return QueryResult(
            columns=["id", "name", "email"],
            rows=[
                (1, "Alice", "alice@example.com"),
                (2, "Bob", "bob@example.com"),
            ],
            row_count=2,
        )

    def test_export_string(self, exporter: JsonExporter, sample_result: QueryResult):
        output = exporter.export_string(sample_result)

        data = json.loads(output)
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[0]["name"] == "Alice"
        assert data[1]["email"] == "bob@example.com"

    def test_export_to_file(
        self, exporter: JsonExporter, sample_result: QueryResult, tmp_path: Path
    ):
        output_path = tmp_path / "output.json"

        exporter.export(sample_result, output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert len(data) == 2

    def test_export_empty_result(self, exporter: JsonExporter):
        result = QueryResult(columns=["id"], rows=[], row_count=0)

        output = exporter.export_string(result)

        data = json.loads(output)
        assert data == []

    def test_export_with_none_values(self, exporter: JsonExporter):
        result = QueryResult(
            columns=["id", "name"],
            rows=[(1, None), (2, "Bob")],
            row_count=2,
        )

        output = exporter.export_string(result)

        data = json.loads(output)
        assert data[0]["name"] is None
        assert data[1]["name"] == "Bob"

    def test_export_with_datetime(self, exporter: JsonExporter):
        from datetime import datetime

        result = QueryResult(
            columns=["id", "created_at"],
            rows=[(1, datetime(2024, 1, 15, 10, 30, 0))],
            row_count=1,
        )

        output = exporter.export_string(result)

        # Should not raise, datetime should be converted to string
        data = json.loads(output)
        assert "2024" in data[0]["created_at"]
