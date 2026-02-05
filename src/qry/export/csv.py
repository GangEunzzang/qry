"""CSV exporter."""

import csv
import io
from pathlib import Path

from qry.export.base import Exporter
from qry.query.result import QueryResult


class CsvExporter(Exporter):
    """Export query results to CSV format."""

    def export(self, result: QueryResult, path: Path) -> None:
        """Export to CSV file."""
        with open(path, "w", newline="") as f:
            self._write_csv(result, f)

    def export_string(self, result: QueryResult) -> str:
        """Export to CSV string."""
        output = io.StringIO()
        self._write_csv(result, output)
        return output.getvalue()

    def _write_csv(self, result: QueryResult, file) -> None:
        """Write CSV data to file-like object."""
        writer = csv.writer(file)
        writer.writerow(result.columns)
        writer.writerows(result.rows)
