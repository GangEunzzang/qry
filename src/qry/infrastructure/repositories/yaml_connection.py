"""YAML-based connection repository implementation."""

from pathlib import Path

import yaml

from qry.domains.connection.models import ConnectionConfig
from qry.domains.connection.repository import ConnectionRepository
from qry.shared.paths import get_config_dir


class YamlConnectionRepository(ConnectionRepository):
    """Persists connection configurations to YAML file."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or (get_config_dir() / "connections.yaml")

    def load_all(self) -> list[ConnectionConfig]:
        if not self._path.exists():
            return []

        try:
            with open(self._path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return []

        configs = []
        for conn_data in data.get("connections", []):
            try:
                configs.append(ConnectionConfig.from_dict(conn_data))
            except (KeyError, ValueError):
                continue
        return configs

    def save_all(self, configs: list[ConnectionConfig]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"connections": [conn.to_dict() for conn in configs]}
        with open(self._path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
