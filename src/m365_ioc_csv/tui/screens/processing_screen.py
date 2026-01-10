"""
Processing screen for CSV parsing and IoC detection.

Shows progress during file processing and displays results.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Label,
    ProgressBar,
    Static,
)

from m365_ioc_csv.core.config import Settings
from m365_ioc_csv.core.csv_parser import CSVParser
from m365_ioc_csv.core.ioc_detector import IoCDetector, IoCType
from m365_ioc_csv.core.csv_writer import CSVWriter, OutputMode
from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingScreen(Screen):
    """
    Screen for processing CSV file and generating output.

    Features:
    - Progress indication
    - Real-time status updates
    - Results summary
    - Navigation options
    """

    CSS = """
    ProcessingScreen {
        layout: vertical;
    }

    #status-container {
        height: 20%;
        padding: 1 2;
        content-align: center middle;
    }

    #progress-container {
        height: 15%;
        padding: 1 2;
    }

    #results-container {
        height: 50%;
    }

    #action-container {
        height: 15%;
        align: center middle;
    }

    ProgressBar {
        width: 100%;
    }

    DataTable {
        height: 1fr;
    }

    .status-text {
        text-align: center;
        text-style: bold;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }
    """

    def __init__(
        self,
        input_file: Path,
        settings: Settings,
        skip_header: str | bool = "auto",
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Initialize processing screen.

        Args:
            input_file: Path to input CSV file
            settings: Application settings
            skip_header: Whether to skip header row (True/False/"auto")
        """
        super().__init__(*args, **kwargs)
        self.input_file = input_file
        self.settings = settings
        self.skip_header = skip_header
        self.parser = CSVParser()
        self.detector = IoCDetector()
        self.writer = CSVWriter(settings)
        self.result_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        with Container(id="status-container"):
            yield Label("Initializing...", id="status-label", classes="status-text")

        with Container(id="progress-container"):
            yield ProgressBar(total=100, show_eta=False, id="progress-bar")

        with Container(id="results-container"):
            yield Static("Processing Results", id="results-title")
            yield DataTable(id="results-table")

        with Container(id="action-container"):
            yield Button("Back to Main", id="back-btn")
            yield Button("Open Output Folder", id="open-folder-btn")

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Setup results table
        table = self.query_one("#results-table", DataTable)
        table.add_column("Stage", width=30)
        table.add_column("Status", width=20)
        table.add_column("Details", width=50)

        # Start processing
        self._start_processing()

    @work(exclusive=True)
    async def _start_processing(self) -> None:
        """Start the processing workflow."""
        try:
            # Stage 1: Parse CSV
            await self._update_progress(10, "Parsing CSV file...")
            parse_result = await asyncio.to_thread(
                self.parser.parse,
                self.input_file,
                skip_header=self.skip_header
            )

            await self._update_result_row("CSV Parsing", "Complete",
                                         f"{parse_result.total_rows} rows, {len(parse_result.ioc_values)} values")

            # Stage 2: Detect IoC types
            await self._update_progress(30, "Detecting IoC types...")
            ioc_dict: dict[str, list[str]] = {
                IoCType.FILE_SHA256.value: [],
                IoCType.FILE_SHA1.value: [],
                IoCType.IP_ADDRESS.value: [],
                IoCType.DOMAIN_NAME.value: [],
                IoCType.URL.value: [],
            }

            unknown_values = []

            for value in parse_result.ioc_values:
                match = self.detector.detect(value)

                if match.type == IoCType.URL_NO_SCHEME:
                    # Auto-fix URL
                    fixed_url = self.detector.fix_url_scheme(
                        value,
                        self.settings.url_prefix_scheme
                    )
                    ioc_dict[IoCType.URL.value].append(fixed_url)
                elif match.type == IoCType.UNKNOWN:
                    unknown_values.append(value)
                elif match.is_valid:
                    ioc_dict[match.type.value].append(value)

            # Show detection results
            total_detected = sum(len(v) for v in ioc_dict.values())
            await self._update_result_row("IoC Detection", "Complete",
                                         f"{total_detected} IoCs detected")

            # Stage 3: Write CSV files
            await self._update_progress(60, "Writing CSV files...")

            output_dir = self.settings.output_dir
            output_mode = OutputMode(self.settings.output_mode)

            write_result = await asyncio.to_thread(
                self.writer.write_iocs,
                ioc_dict,
                output_dir,
                output_mode,
                self.input_file.name
            )

            await self._update_result_row("CSV Generation", "Complete",
                                         f"{write_result.total_files} files created")

            # Stage 4: Handle unknown values
            if unknown_values:
                await self._update_progress(90, "Writing unknown values...")
                unknown_file = await asyncio.to_thread(
                    self.writer.write_unknown_iocs,
                    unknown_values,
                    output_dir
                )
                if unknown_file:
                    await self._update_result_row("Unknown Values", "Saved",
                                                 f"{len(unknown_values)} values to {unknown_file.name}")

            # Complete
            await self._update_progress(100, "Processing complete!")
            status_label = self.query_one("#status-label", Label)
            status_label.add_class("success")
            status_label.update("✓ Processing Complete!")

            # Show file list
            await self._show_output_files(write_result.files_written)

            # Update main screen with counts (if it exists in screen stack)
            try:
                # Search in screen stack for MainScreen
                for screen in self.app.screen_stack:
                    from m365_ioc_csv.tui.screens.main_screen import MainScreen
                    if isinstance(screen, MainScreen):
                        if hasattr(screen, 'update_ioc_counts'):
                            screen.update_ioc_counts({k: len(v) for k, v in ioc_dict.items()})
                        break
            except Exception:
                # MainScreen might not be in stack, this is okay
                pass

        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            await self._update_progress(0, "Processing failed!")
            status_label = self.query_one("#status-label", Label)
            status_label.add_class("error")
            status_label.update(f"✗ Error: {e}")
            await self._update_result_row("Error", "Failed", str(e))

    async def _update_progress(self, progress: float, status: str) -> None:
        """Update progress bar and status."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        status_label = self.query_one("#status-label", Label)

        progress_bar.update(progress=progress)
        status_label.update(status)

    async def _update_result_row(self, stage: str, status: str, details: str) -> None:
        """Add/update row in results table."""
        table = self.query_one("#results-table", DataTable)

        # Check if stage already exists by getting cell value
        # We need to iterate through rows and check the first column
        row_key = None
        for row in table.rows:
            # Get the cell value at column 0 for this row
            try:
                cell_value = table.get_cell(row, 0)
                if cell_value == stage:
                    row_key = row
                    break
            except Exception:
                # If we can't get the cell, skip this row
                continue

        # Update existing row or add new one
        if row_key is not None:
            table.update_cell(row_key, 1, status)
            table.update_cell(row_key, 2, details)
        else:
            # Add new row
            table.add_row(stage, status, details)

    async def _show_output_files(self, files: list[Path]) -> None:
        """Add output files to results table."""
        table = self.query_one("#results-table", DataTable)

        table.add_row("", "", "")  # Separator
        table.add_row("Output Files", "", "")

        for file_path in files:
            table.add_row("", f"📄 {file_path.name}", str(file_path.parent))

    @on(Button.Pressed, "#back-btn")
    def on_back_pressed(self) -> None:
        """Handle back button press."""
        self.app.pop_screen()

    @on(Button.Pressed, "#open-folder-btn")
    def on_open_folder_pressed(self) -> None:
        """Handle open folder button press."""
        import platform
        import subprocess

        output_dir = self.settings.output_dir

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(output_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])

            self.notify(f"Opened {output_dir}", severity="information")
        except Exception as e:
            self.notify(f"Could not open folder: {e}", severity="error")
            logger.warning(f"Could not open folder: {e}")
