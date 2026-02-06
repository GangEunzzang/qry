"""JSON exporter."""

import json
from pathlib import Path
from typing import Any

from qry.domains.export.base import Exporter
from qry.shared.models import QueryResult


class JsonExporter(Exporter):
    def export(self, result: QueryResult, path: Path) -> None:
        with open(path, "w") as f:
            json.dump(self._to_dict(result), f, indent=2, default=str)

    def export_string(self, result: QueryResult) -> str:
        return json.dumps(self._to_dict(result), indent=2, default=str)

    def _to_dict(self, result: QueryResult) -> list[dict[str, Any]]:
        return [dict(zip(result.columns, row, strict=True)) for row in result.rows]
