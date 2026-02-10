"""Export modal screen."""

from datetime import datetime
from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, RadioButton, RadioSet

from qry.domains.export.base import Exporter
from qry.domains.export.csv import CsvExporter
from qry.domains.export.json import JsonExporter
from qry.domains.export.markdown import MarkdownExporter
from qry.shared.models import QueryResult


class ExportScreen(ModalScreen[str | None]):
    """Modal screen for exporting query results."""

    DEFAULT_CSS = """
    ExportScreen {
        align: center middle;
    }

    #export-dialog {
        width: 60;
        height: auto;
        max-height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #export-dialog Label {
        margin-bottom: 1;
    }

    #format-group {
        height: auto;
        margin-bottom: 1;
    }

    #file-path {
        margin-bottom: 1;
    }

    #button-row {
        height: 3;
        align: right middle;
    }

    #button-row Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    _EXPORTERS: ClassVar[dict[str, type[Exporter]]] = {
        "csv": CsvExporter,
        "json": JsonExporter,
        "md": MarkdownExporter,
    }

    def __init__(self, result: QueryResult) -> None:
        super().__init__()
        self._result = result
        self._format = "csv"

    def compose(self) -> ComposeResult:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = str(Path.home() / "Downloads" / f"query_result_{timestamp}.csv")

        with Vertical(id="export-dialog"):
            yield Label("Export Results")
            with RadioSet(id="format-group"):
                yield RadioButton("CSV", value=True, id="fmt-csv")
                yield RadioButton("JSON", id="fmt-json")
                yield RadioButton("Markdown", id="fmt-md")
            yield Input(value=default_path, placeholder="File path", id="file-path")
            with Horizontal(id="button-row"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Export", variant="primary", id="btn-export")

    _FORMAT_MAP: ClassVar[dict[str, str]] = {
        "fmt-csv": "csv",
        "fmt-json": "json",
        "fmt-md": "md",
    }

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        pressed = event.radio_set.pressed_button
        if not pressed:
            return
        fmt = self._FORMAT_MAP.get(pressed.id or "", "csv")
        old_fmt = self._format
        self._format = fmt

        path_input = self.query_one("#file-path", Input)
        current_path = Path(path_input.value)
        known_exts = {".csv", ".json", ".md"}
        if current_path.suffix in known_exts:
            path_input.value = str(current_path.with_suffix(f".{fmt}"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-export":
            self._do_export()

    def _do_export(self) -> None:
        path_input = self.query_one("#file-path", Input)
        path_str = path_input.value.strip()
        if not path_str:
            self.app.notify("Please enter a file path", severity="error")
            return

        path = Path(path_str).expanduser()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            exporter = self._EXPORTERS[self._format]()
            exporter.export(self._result, path)
            self.dismiss(str(path))
        except OSError as e:
            self.app.notify(f"Export failed: {e}", severity="error")

    def action_cancel(self) -> None:
        self.dismiss(None)
