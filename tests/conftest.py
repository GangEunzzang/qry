"""Pytest configuration and fixtures."""

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create temporary config directory and patch paths."""
    config_dir = tmp_path / ".qry"
    config_dir.mkdir()
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Patch the paths module - both in shared.paths and where they're imported
    monkeypatch.setattr("qry.shared.paths.get_config_dir", lambda: config_dir)
    monkeypatch.setattr("qry.shared.paths.get_data_dir", lambda: data_dir)
    monkeypatch.setattr("qry.shared.paths.get_cache_dir", lambda: tmp_path / "cache")

    # Patch in infrastructure repositories that import paths
    monkeypatch.setattr(
        "qry.infrastructure.repositories.yaml_connection.get_config_dir", lambda: config_dir
    )
    monkeypatch.setattr(
        "qry.infrastructure.repositories.json_history.get_data_dir", lambda: data_dir
    )

    return config_dir


@pytest.fixture
def sample_sqlite_db(tmp_path: Path) -> Path:
    """Create sample SQLite database for testing."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
    conn.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT)")
    conn.execute("INSERT INTO posts VALUES (1, 1, 'Hello World')")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_sqlite_db(tmp_path: Path) -> Path:
    """Create empty SQLite database for testing."""
    db_path = tmp_path / "empty.db"
    conn = sqlite3.connect(db_path)
    conn.close()
    return db_path
