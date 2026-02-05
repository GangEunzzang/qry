"""Configuration paths utilities."""

from pathlib import Path


def get_config_dir() -> Path:
    """Get configuration directory path.

    Checks ~/.qry/ first, then ~/.config/qry/.

    Returns:
        Path to configuration directory.
    """
    qry_dir = Path.home() / ".qry"
    if qry_dir.exists():
        return qry_dir

    config_dir = Path.home() / ".config" / "qry"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    """Get data directory path (for history, etc.).

    Returns:
        Path to data directory.
    """
    data_dir = Path.home() / ".local" / "share" / "qry"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir() -> Path:
    """Get cache directory path.

    Returns:
        Path to cache directory.
    """
    cache_dir = Path.home() / ".cache" / "qry"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
