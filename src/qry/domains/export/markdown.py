"""Markdown table exporter."""

from pathlib import Path

from qry.domains.export.base import Exporter
from qry.shared.models import QueryResult

NULL_DISPLAY = "NULL"


class MarkdownExporter(Exporter):
    def __init__(self, null_display: str = NULL_DISPLAY) -> None:
        self._null_display = null_display

    def export(self, result: QueryResult, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.export_string(result))

    def export_string(self, result: QueryResult) -> str:
        if not result.columns:
            return ""

        columns = result.columns
        str_rows = [
            [self._escape(self._format_value(v)) for v in row]
            for row in result.rows
        ]
        escaped_headers = [self._escape(col) for col in columns]

        # Calculate column widths (minimum 3 for separator dashes)
        widths = [max(3, len(h)) for h in escaped_headers]
        for row in str_rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(val))

        # Build header
        header = (
            "| "
            + " | ".join(
                h.ljust(w) for h, w in zip(escaped_headers, widths, strict=True)
            )
            + " |"
        )
        separator = "|" + "|".join("-" * (w + 2) for w in widths) + "|"

        lines = [header, separator]
        for row in str_rows:
            line = (
                "| "
                + " | ".join(
                    v.ljust(w) for v, w in zip(row, widths, strict=True)
                )
                + " |"
            )
            lines.append(line)

        return "\n".join(lines) + "\n"

    def _format_value(self, value: object) -> str:
        if value is None:
            return self._null_display
        return str(value)

    def _escape(self, text: str) -> str:
        """Escape pipe characters in markdown table cells."""
        return text.replace("|", "\\|").replace("\n", " ").replace("\r", "")
