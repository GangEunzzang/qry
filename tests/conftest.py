"""Pytest configuration and fixtures."""

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory."""
    config_dir = tmp_path / ".qry"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_sqlite_db(tmp_path: Path) -> Path:
    """Create sample SQLite database for testing."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()
    return db_path
