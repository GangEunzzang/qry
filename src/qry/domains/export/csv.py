"""CSV exporter."""

import csv
import io
from pathlib import Path

from qry.domains.export.base import Exporter
from qry.domains.query.models import QueryResult


class CsvExporter(Exporter):
    def export(self, result: QueryResult, path: Path) -> None:
        with open(path, "w", newline="") as f:
            self._write_csv(result, f)

    def export_string(self, result: QueryResult) -> str:
        output = io.StringIO()
        self._write_csv(result, output)
        return output.getvalue()

    def _write_csv(self, result: QueryResult, file) -> None:
        writer = csv.writer(file)
        writer.writerow(result.columns)
        writer.writerows(result.rows)
