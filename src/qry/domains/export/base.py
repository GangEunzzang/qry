"""Base exporter interface."""

from abc import ABC, abstractmethod
from pathlib import Path

from qry.shared.models import QueryResult


class Exporter(ABC):
    """Abstract base class for exporters."""

    @abstractmethod
    def export(self, result: QueryResult, path: Path) -> None:
        pass

    @abstractmethod
    def export_string(self, result: QueryResult) -> str:
        pass
