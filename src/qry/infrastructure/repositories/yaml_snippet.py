"""YAML-based snippet repository implementation."""

from datetime import datetime
from pathlib import Path

import yaml

from qry.domains.snippet.models import Snippet
from qry.domains.snippet.repository import SnippetRepository
from qry.shared.paths import get_config_dir


class YamlSnippetRepository(SnippetRepository):
    """Persists SQL snippets to YAML file."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (get_config_dir() / "snippets.yaml")

    def list_all(self) -> list[Snippet]:
        if not self._path.exists():
            return []

        try:
            with open(self._path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return []

        snippets: list[Snippet] = []
        for item in data.get("snippets", []):
            try:
                created_at = item.get("created_at")
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                elif not isinstance(created_at, datetime):
                    created_at = datetime.now()

                snippets.append(
                    Snippet(
                        name=item["name"],
                        query=item["query"],
                        description=item.get("description", ""),
                        category=item.get("category", ""),
                        created_at=created_at,
                    )
                )
            except (KeyError, ValueError):
                continue
        return snippets

    def get(self, name: str) -> Snippet | None:
        for snippet in self.list_all():
            if snippet.name == name:
                return snippet
        return None

    def save(self, snippet: Snippet) -> None:
        snippets = self.list_all()
        existing = next((i for i, s in enumerate(snippets) if s.name == snippet.name), None)
        if existing is not None:
            snippets[existing] = snippet
        else:
            snippets.append(snippet)
        self._write(snippets)

    def delete(self, name: str) -> bool:
        snippets = self.list_all()
        filtered = [s for s in snippets if s.name != name]
        if len(filtered) == len(snippets):
            return False
        self._write(filtered)
        return True

    def _write(self, snippets: list[Snippet]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "snippets": [
                {
                    "name": s.name,
                    "query": s.query,
                    "description": s.description,
                    "category": s.category,
                    "created_at": s.created_at.isoformat(),
                }
                for s in snippets
            ]
        }
        with open(self._path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
