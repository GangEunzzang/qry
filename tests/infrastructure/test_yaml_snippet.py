"""Tests for YamlSnippetRepository."""

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from qry.domains.snippet.models import Snippet
from qry.infrastructure.repositories.yaml_snippet import YamlSnippetRepository


class TestYamlSnippetRepository:
    @pytest.fixture
    def repo(self, tmp_path: Path) -> YamlSnippetRepository:
        return YamlSnippetRepository(path=tmp_path / "snippets.yaml")

    @pytest.fixture
    def sample_snippet(self) -> Snippet:
        return Snippet(
            name="select_users",
            query="SELECT * FROM users",
            description="Get all users",
            category="queries",
            created_at=datetime(2024, 6, 15, 12, 0, 0),
        )

    def test_list_all_empty(self, repo: YamlSnippetRepository):
        assert repo.list_all() == []

    def test_save_and_list(self, repo: YamlSnippetRepository, sample_snippet: Snippet):
        repo.save(sample_snippet)
        snippets = repo.list_all()
        assert len(snippets) == 1
        assert snippets[0].name == "select_users"
        assert snippets[0].query == "SELECT * FROM users"
        assert snippets[0].description == "Get all users"
        assert snippets[0].category == "queries"

    def test_save_multiple(self, repo: YamlSnippetRepository):
        s1 = Snippet(name="first", query="SELECT 1")
        s2 = Snippet(name="second", query="SELECT 2")
        repo.save(s1)
        repo.save(s2)
        snippets = repo.list_all()
        assert len(snippets) == 2
        names = [s.name for s in snippets]
        assert "first" in names
        assert "second" in names

    def test_save_update_existing(self, repo: YamlSnippetRepository, sample_snippet: Snippet):
        repo.save(sample_snippet)
        updated = Snippet(
            name="select_users",
            query="SELECT id, name FROM users",
            description="Updated",
            category="queries",
        )
        repo.save(updated)
        snippets = repo.list_all()
        assert len(snippets) == 1
        assert snippets[0].query == "SELECT id, name FROM users"
        assert snippets[0].description == "Updated"

    def test_get_existing(self, repo: YamlSnippetRepository, sample_snippet: Snippet):
        repo.save(sample_snippet)
        result = repo.get("select_users")
        assert result is not None
        assert result.name == "select_users"
        assert result.query == "SELECT * FROM users"

    def test_get_nonexistent(self, repo: YamlSnippetRepository):
        result = repo.get("nonexistent")
        assert result is None

    def test_delete_existing(self, repo: YamlSnippetRepository, sample_snippet: Snippet):
        repo.save(sample_snippet)
        deleted = repo.delete("select_users")
        assert deleted is True
        assert repo.list_all() == []

    def test_delete_nonexistent(self, repo: YamlSnippetRepository):
        deleted = repo.delete("nonexistent")
        assert deleted is False

    def test_delete_preserves_others(self, repo: YamlSnippetRepository):
        s1 = Snippet(name="keep", query="SELECT 1")
        s2 = Snippet(name="remove", query="SELECT 2")
        repo.save(s1)
        repo.save(s2)
        repo.delete("remove")
        snippets = repo.list_all()
        assert len(snippets) == 1
        assert snippets[0].name == "keep"

    def test_yaml_file_format(self, repo: YamlSnippetRepository, tmp_path: Path):
        snippet = Snippet(
            name="test",
            query="SELECT 1",
            description="desc",
            category="cat",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        repo.save(snippet)
        with open(tmp_path / "snippets.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "snippets" in data
        assert len(data["snippets"]) == 1
        assert data["snippets"][0]["name"] == "test"
        assert data["snippets"][0]["query"] == "SELECT 1"

    def test_corrupted_yaml_returns_empty(self, tmp_path: Path):
        path = tmp_path / "snippets.yaml"
        path.write_text("{{invalid yaml", encoding="utf-8")
        repo = YamlSnippetRepository(path=path)
        assert repo.list_all() == []

    def test_missing_required_fields_skipped(self, tmp_path: Path):
        path = tmp_path / "snippets.yaml"
        data = {
            "snippets": [
                {"name": "valid", "query": "SELECT 1"},
                {"name": "no_query"},  # missing query field
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        repo = YamlSnippetRepository(path=path)
        snippets = repo.list_all()
        assert len(snippets) == 1
        assert snippets[0].name == "valid"

    def test_creates_parent_directories(self, tmp_path: Path):
        path = tmp_path / "nested" / "dir" / "snippets.yaml"
        repo = YamlSnippetRepository(path=path)
        repo.save(Snippet(name="test", query="SELECT 1"))
        assert path.exists()
