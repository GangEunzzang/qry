"""JSON exporter."""

import json
from pathlib import Path
from typing import Any

from qry.export.base import Exporter
from qry.query.result import QueryResult


class JsonExporter(Exporter):
    """Export query results to JSON format."""

    def export(self, result: QueryResult, path: Path) -> None:
        """Export to JSON file."""
        with open(path, "w") as f:
            json.dump(self._to_dict(result), f, indent=2, default=str)

    def export_string(self, result: QueryResult) -> str:
        """Export to JSON string."""
        return json.dumps(self._to_dict(result), indent=2, default=str)

    def _to_dict(self, result: QueryResult) -> list[dict[str, Any]]:
        """Convert result to list of dictionaries."""
        return [dict(zip(result.columns, row)) for row in result.rows]
