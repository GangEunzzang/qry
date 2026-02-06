"""Configuration paths utilities."""

from pathlib import Path


def get_config_dir() -> Path:
    qry_dir = Path.home() / ".qry"
    if qry_dir.exists():
        return qry_dir

    config_dir = Path.home() / ".config" / "qry"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    data_dir = Path.home() / ".local" / "share" / "qry"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".cache" / "qry"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
