"""Tests for exporters."""

import json
from pathlib import Path

import pytest

from qry.domains.export.csv import CsvExporter
from qry.domains.export.json import JsonExporter
from qry.domains.export.markdown import MarkdownExporter
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


class TestMarkdownExporter:
    @pytest.fixture
    def exporter(self) -> MarkdownExporter:
        return MarkdownExporter()

    @pytest.fixture
    def sample_result(self) -> QueryResult:
        return QueryResult(
            columns=["name", "email", "age"],
            rows=[
                ("Alice", "alice@example.com", 30),
                ("Bob", "bob@example.com", 25),
            ],
            row_count=2,
        )

    def test_export_string(
        self, exporter: MarkdownExporter, sample_result: QueryResult
    ):
        output = exporter.export_string(sample_result)
        lines = output.strip().split("\n")

        assert len(lines) == 4  # header + separator + 2 data rows
        assert "| name" in lines[0]
        assert "| email" in lines[0]
        assert "| age" in lines[0]
        assert lines[1].startswith("|")
        assert "---" in lines[1]
        assert "Alice" in lines[2]
        assert "Bob" in lines[3]

    def test_export_to_file(
        self,
        exporter: MarkdownExporter,
        sample_result: QueryResult,
        tmp_path: Path,
    ):
        output_path = tmp_path / "output.md"

        exporter.export(sample_result, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "Alice" in content
        assert "---" in content

    def test_export_empty_result(self, exporter: MarkdownExporter):
        result = QueryResult(columns=["id"], rows=[], row_count=0)

        output = exporter.export_string(result)
        lines = output.strip().split("\n")

        # Header + separator, no data rows
        assert len(lines) == 2
        assert "| id" in lines[0]

    def test_export_empty_columns(self, exporter: MarkdownExporter):
        result = QueryResult(columns=[], rows=[], row_count=0)

        output = exporter.export_string(result)

        assert output == ""

    def test_null_handling(self, exporter: MarkdownExporter):
        result = QueryResult(
            columns=["id", "name"],
            rows=[(1, None), (2, "Bob")],
            row_count=2,
        )

        output = exporter.export_string(result)

        assert "NULL" in output
        assert "Bob" in output

    def test_null_custom_display(self):
        exporter = MarkdownExporter(null_display="(empty)")
        result = QueryResult(
            columns=["id", "name"],
            rows=[(1, None)],
            row_count=1,
        )

        output = exporter.export_string(result)

        assert "(empty)" in output

    def test_column_width_auto_adjust(self, exporter: MarkdownExporter):
        result = QueryResult(
            columns=["x", "long_column_name"],
            rows=[("short", "v")],
            row_count=1,
        )

        output = exporter.export_string(result)
        lines = output.strip().split("\n")

        # Header and separator cells should have matching widths
        header_parts = lines[0].split("|")
        sep_parts = lines[1].split("|")
        for h, s in zip(header_parts[1:-1], sep_parts[1:-1], strict=True):
            assert len(h) == len(s)

    def test_special_chars_pipe_escape(self, exporter: MarkdownExporter):
        result = QueryResult(
            columns=["data"],
            rows=[("val|ue",)],
            row_count=1,
        )

        output = exporter.export_string(result)

        # Pipe inside cell should be escaped
        assert "val\\|ue" in output
