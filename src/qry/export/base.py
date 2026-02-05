"""Base exporter interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from qry.query.result import QueryResult


class Exporter(ABC):
    """Abstract base class for exporters."""

    @abstractmethod
    def export(self, result: QueryResult, path: Path) -> None:
        """Export query result to file.

        Args:
            result: Query result to export.
            path: Output file path.
        """

    @abstractmethod
    def export_string(self, result: QueryResult) -> str:
        """Export query result to string.

        Args:
            result: Query result to export.

        Returns:
            Exported data as string.
        """
