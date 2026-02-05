"""Settings module."""

from qry.settings.config import EditorSettings, HistorySettings, ResultsSettings, Settings
from qry.settings.paths import get_cache_dir, get_config_dir, get_data_dir

__all__ = [
    "Settings",
    "EditorSettings",
    "ResultsSettings",
    "HistorySettings",
    "get_config_dir",
    "get_data_dir",
    "get_cache_dir",
]
