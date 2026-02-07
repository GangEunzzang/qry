"""Application settings."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from qry.shared.constants import (
    DEFAULT_HISTORY_SIZE,
    DEFAULT_MAX_COLUMN_WIDTH,
    DEFAULT_PAGE_SIZE,
    DEFAULT_TAB_SIZE,
    DEFAULT_THEME,
    NULL_DISPLAY,
)
from qry.shared.paths import get_config_dir


@dataclass
class EditorSettings:
    tab_size: int = DEFAULT_TAB_SIZE
    show_line_numbers: bool = True
    highlight_current_line: bool = True
    vim_mode: bool = False
    inline_errors: bool = True


@dataclass
class ResultsSettings:
    max_column_width: int = DEFAULT_MAX_COLUMN_WIDTH
    null_display: str = NULL_DISPLAY
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass
class HistorySettings:
    max_entries: int = DEFAULT_HISTORY_SIZE
    save_on_exit: bool = True


@dataclass
class Settings:
    theme: str = DEFAULT_THEME
    confirm_exit: bool = True
    editor: EditorSettings = field(default_factory=EditorSettings)
    results: ResultsSettings = field(default_factory=ResultsSettings)
    history: HistorySettings = field(default_factory=HistorySettings)

    @classmethod
    def load(cls, path: Path | None = None) -> "Settings":
        if path is None:
            path = get_config_dir() / "config.toml"

        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "Settings":
        general = data.get("general", {})
        editor_data = data.get("editor", {})
        results_data = data.get("results", {})
        history_data = data.get("history", {})

        return cls(
            theme=general.get("theme", DEFAULT_THEME),
            confirm_exit=general.get("confirm_exit", True),
            editor=EditorSettings(
                tab_size=editor_data.get("tab_size", DEFAULT_TAB_SIZE),
                show_line_numbers=editor_data.get("show_line_numbers", True),
                highlight_current_line=editor_data.get("highlight_current_line", True),
                vim_mode=editor_data.get("vim_mode", False),
                inline_errors=editor_data.get("inline_errors", True),
            ),
            results=ResultsSettings(
                max_column_width=results_data.get("max_column_width", DEFAULT_MAX_COLUMN_WIDTH),
                null_display=results_data.get("null_display", NULL_DISPLAY),
                page_size=results_data.get("page_size", DEFAULT_PAGE_SIZE),
            ),
            history=HistorySettings(
                max_entries=history_data.get("max_entries", DEFAULT_HISTORY_SIZE),
                save_on_exit=history_data.get("save_on_exit", True),
            ),
        )

    def save(self, path: Path | None = None) -> None:
        if path is None:
            path = get_config_dir() / "config.toml"

        path.parent.mkdir(parents=True, exist_ok=True)

        content = f'''# qry configuration

[general]
theme = "{self.theme}"
confirm_exit = {str(self.confirm_exit).lower()}

[editor]
tab_size = {self.editor.tab_size}
show_line_numbers = {str(self.editor.show_line_numbers).lower()}
highlight_current_line = {str(self.editor.highlight_current_line).lower()}
vim_mode = {str(self.editor.vim_mode).lower()}
inline_errors = {str(self.editor.inline_errors).lower()}

[results]
max_column_width = {self.results.max_column_width}
null_display = "{self.results.null_display}"
page_size = {self.results.page_size}

[history]
max_entries = {self.history.max_entries}
save_on_exit = {str(self.history.save_on_exit).lower()}
'''
        path.write_text(content)
