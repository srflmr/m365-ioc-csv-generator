"""
Main screen for the M365 IOC CSV Generator application.

Provides the primary interface with:
- File selection/directory browser
- File info display (format, header detection)
- Configuration options
- Summary display
- Action buttons
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    DirectoryTree,
    Label,
    Select,
    Input,
    DataTable,
    ProgressBar,
    Header,
    Footer,
    Static,
)

from m365_ioc_csv.core.config import Settings, Action, Severity
from m365_ioc_csv.core.csv_parser import CSVParser

from m365_ioc_csv.core.excel_parser import ExcelParser, ExcelParseResult, ExcelSheetInfo
from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


class MainScreen(Screen):
    """
    Main application screen.

    Layout:
    +------------------------------------------+
    |               HEADER                     |
    +------------------------------------------+
    |  FILE BROWSER  |  FILE INFO & CONFIG     |
    |                |                        |
    |                |                        |
    +------------------------------------------+
    |              SUMMARY PANEL               |
    |                (IoC counts)              |
    +------------------------------------------+
    |      ACTION BUTTONS                      |
    +------------------------------------------+
    |               FOOTER                     |
    +------------------------------------------+
    """

    CSS = """
    /* Main Screen Layout - Modern Responsive Grid System */
    MainScreen {
        layout: grid;
        grid-size: 2 3;  /* 2 columns, 3 rows */
        grid-columns: 1fr 2fr;  /* Left panel 1/3, right panel 2/3 */
        grid-rows: auto 1fr auto;  /* Header auto, middle flexible, actions auto */
        grid-gutter: 1 2;  /* Vertical 1, horizontal 2 (for terminal aspect ratio) */
    }

    /* Panels - Responsive with fractional units */
    #file-browser-panel {
        height: 100%;
        row-span: 2;  /* Span middle rows */
        border: thick $primary;
        border-title-color: $accent;
        border-title-style: bold;
    }

    #info-config-panel {
        layout: vertical;
        height: 100%;
    }

    /* File Info Section - Auto height based on content */
    #file-info-container {
        height: auto;
        max-height: 40%;
        border: thick $primary;
        border-title-color: $success;
        overflow-y: auto;
    }

    #file-info-title {
        text-style: bold;
        color: $success;
        padding: 0 1;
        dock: top;
    }

    /* Info Labels - Auto sizing */
    .info-row {
        height: auto;
        padding: 0 1;
        layout: horizontal;
    }

    .info-label {
        width: auto;  /* Auto width based on content */
        min-width: 20;  /* Minimum width for readability */
        text-align: right;
        padding: 1 1;
        text-style: bold;
        color: $text;
    }

    .info-value {
        width: 1fr;  /* Take remaining space */
        padding: 1 1;
        color: $text-muted;
    }

    .header-detected {
        text-style: bold;
        color: $success;
    }

    .header-not-detected {
        text-style: italic;
        color: $warning;
    }

    /* Configuration Section - Flexible scrolling */
    #config-container {
        height: 1fr;  /* Take remaining vertical space */
        border: thick $primary;
        border-title-color: $accent;
        overflow-y: auto;
    }

    #config-title {
        text-style: bold;
        color: $accent;
        padding: 0 1;
        dock: top;
    }

    /* Config Rows - Responsive horizontal layout */
    .config-row {
        height: auto;
        padding: 1;
        layout: horizontal;
        align: center middle;
    }

    .config-label {
        width: auto;  /* Auto width based on label text */
        min-width: 25;  /* Minimum width */
        text-align: right;
        padding: 0 1;
        text-style: bold;
    }

    .config-input {
        width: 1fr;  /* Take remaining space */
        min-width: 20;
    }

    /* Select widget styling */
    Select {
        width: 1fr;
    }

    Input {
        width: 1fr;
    }

    /* Directory Tree - Full height of its panel */
    DirectoryTree {
        height: 1fr;
    }

    #file-browser-title {
        text-style: bold;
        color: $accent;
        dock: top;
        padding: 0 1;
    }

    /* Summary Panel - Bottom left */
    #summary-panel {
        border: thick $primary;
        border-title-color: $warning;
        height: 1fr;
    }

    #summary-title {
        text-style: bold;
        color: $warning;
        dock: top;
        padding: 0 1;
    }

    DataTable {
        height: 1fr;
    }

    /* Action Buttons - Responsive grid */
    #action-container {
        column-span: 2;  /* Span all columns */
        height: auto;
        layout: grid;
        grid-size: 4;  /* 4 columns for buttons */
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-gutter: 1;
        padding: 1 0;
    }

    Button {
        min-width: 15;
        height: 3;
        margin: 0;
    }

    /* Header and Footer */
    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the main screen."""
        super().__init__(*args, **kwargs)
        self.settings = Settings()
        self.selected_file: Optional[Path] = None
        self.ioc_counts: dict[str, int] = {}
        self.file_info: dict[str, Any] = {}
        self.skip_header: str | bool = "auto"

    def compose(self) -> ComposeResult:
        """Compose the UI with modern responsive grid layout."""
        # Header and Footer are docked
        yield Header()
        yield Footer()

        # === CELL 1: File Browser Panel (Left, spans 2 rows) ===
        with Container(id="file-browser-panel"):
            yield Static("📁 Select CSV File", id="file-browser-title")
            yield DirectoryTree(".", id="file-tree")

        # === CELL 2: Info & Config Panel (Right, top row) ===
        with Container(id="info-config-panel"):
            # File Info Section
            with ScrollableContainer(id="file-info-container"):
                yield Static("📄 File Information", id="file-info-title")
                yield Label("File: -", id="info-file", classes="info-row")
                yield Label("Delimiter: -", id="info-delimiter", classes="info-row")
                yield Label("Encoding: -", id="info-encoding", classes="info-row")
                yield Label("Total Rows: -", id="info-rows", classes="info-row")
                yield Label("Header: -", id="info-header", classes="info-row")

            # Configuration Section
            with ScrollableContainer(id="config-container"):
                yield Static("⚙️ Configuration", id="config-title")

                # Header handling
                with Horizontal(classes="config-row"):
                    yield Label("Header:", classes="config-label")
                    yield Select(
                        [
                            ("Auto-detect", "auto"),
                            ("Always skip first row", "true"),
                            ("Never skip (include all)", "false"),
                        ],
                        value="auto",
                        id="header-select",
                        classes="config-input"
                    )

                # Action selection
                with Horizontal(classes="config-row"):
                    yield Label("Action:", classes="config-label")
                    yield Select(
                        [(a.value, a.value) for a in Action],
                        value=Action.BLOCK.value,
                        id="action-select",
                        classes="config-input"
                    )

                # Severity selection
                with Horizontal(classes="config-row"):
                    yield Label("Severity:", classes="config-label")
                    yield Select(
                        [(s.value, s.value) for s in Severity],
                        value=Severity.HIGH.value,
                        id="severity-select",
                        classes="config-input"
                    )

                # Custom title
                with Horizontal(classes="config-row"):
                    yield Label("Title:", classes="config-label")
                    yield Input(
                        placeholder="Empty for default",
                        id="custom-title",
                        classes="config-input"
                    )

                # Custom description
                with Horizontal(classes="config-row"):
                    yield Label("Description:", classes="config-label")
                    yield Input(
                        placeholder="Empty for default",
                        id="custom-description",
                        classes="config-input"
                    )

                # Expiration
                with Horizontal(classes="config-row"):
                    yield Label("Expiration:", classes="config-label")
                    yield Select(
                        [
                            ("Never", "never"),
                            ("30 days", "30"),
                            ("90 days", "90"),
                            ("180 days", "180"),
                            ("365 days", "365"),
                        ],
                        value="never",
                        id="expiration-select",
                        classes="config-input"
                    )

                # Generate alert
                with Horizontal(classes="config-row"):
                    yield Label("Alert:", classes="config-label")
                    yield Select(
                        [("Yes", "true"), ("No", "false")],
                        value="true",
                        id="alert-select",
                        classes="config-input"
                    )

                # Note: Output mode is now always "separate" - separate CSV files per IoC type

        # === CELL 3: Summary Panel (Left, bottom row) ===
        with Container(id="summary-panel"):
            yield Static("📊 Summary", id="summary-title")
            yield DataTable(id="summary-table")

        # === CELL 4: Action Buttons (Spans 2 columns at bottom) ===
        with Container(id="action-container"):
            yield Button("▶ Process", variant="primary", id="process-btn")
            yield Button("✕ Clear", id="clear-btn")
            yield Button("↻ Refresh", id="refresh-btn")
            yield Button("⏻ Exit", id="exit-btn")

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Setup summary table
        table = self.query_one("#summary-table", DataTable)
        table.add_column("Property", width=30)
        table.add_column("Value", width=20)

        # Initial empty state
        table.add_row("Selected File", "-")
        table.add_row("Total IoCs", "0")
        table.add_row("FileSha256", "0")
        table.add_row("FileSha1", "0")
        table.add_row("FileMd5", "0")
        table.add_row("IpAddress", "0")
        table.add_row("DomainName", "0")
        table.add_row("Url", "0")

        logger.info("MainScreen mounted")

    @on(DirectoryTree.FileSelected, "#file-tree")
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from directory tree."""
        path = event.path
        logger.info(f"File selected: {path}")

        # Check if it's a directory
        if path.is_dir():
            return

        # Check file type and route accordingly
        if path.suffix.lower() in (".xlsx", ".xls"):
            # Excel file - check if openpyxl is available
            if not self._check_openpyxl_available():
                self.notify(
                    "Excel files require openpyxl package. "
                    "Install with: pip install openpyxl",
                    severity="error"
                )
                return

            # Parse Excel file to get sheet info
            try:
                excel_parser = ExcelParser()
                sheets = excel_parser.get_sheets(path)

                if not sheets:
                    self.notify("No sheets found in Excel file", severity="error")
                    return

                # Push sheet selection screen
                from m365_ioc_csv.tui.screens.sheet_selection_screen import SheetSelectionScreen
                sheet_screen = SheetSelectionScreen(
                    excel_file=path,
                    sheets=sheets,
                    settings=self.settings,
                    skip_header=self.skip_header
                )
                self.app.push_screen(sheet_screen)

            except Exception as e:
                logger.error(f"Error loading Excel file: {e}")
                self.notify(f"Error loading Excel file: {e}", severity="error")
            return

        # CSV-like files
        if path.suffix.lower() not in (".csv", ".tsv", ".txt", ".log"):
            self.notify(f"Invalid file type: {path.suffix}", severity="error")
            return

        self.selected_file = path
        self._analyze_file()

    def _check_openpyxl_available(self) -> bool:
        """Check if openpyxl package is available."""
        try:
            import openpyxl
            return True
        except ImportError:
            return False

    @on(Select.Changed, "#header-select")
    def on_header_select_changed(self, event: Select.Changed) -> None:
        """Handle header selection change."""
        if event.value == "true":
            self.skip_header = True
        elif event.value == "false":
            self.skip_header = False
        else:
            self.skip_header = "auto"

        # Re-analyze if file is selected
        if self.selected_file:
            self._analyze_file()

    def _analyze_file(self) -> None:
        """Analyze the selected file and update info display."""
        if not self.selected_file:
            return

        try:
            parser = CSVParser()
            self.file_info = parser.get_file_info(self.selected_file)

            # Update file info display
            self.query_one("#info-file", Label).update(
                f"File: {self.selected_file.name}"
            )
            self.query_one("#info-delimiter", Label).update(
                f"Delimiter: '{self.file_info['delimiter']}'"
            )
            self.query_one("#info-encoding", Label).update(
                f"Encoding: {self.file_info['encoding']}"
            )
            self.query_one("#info-rows", Label).update(
                f"Total Rows: {self.file_info['total_rows']} "
                f"({self.file_info['data_rows']} data, {self.file_info['skipped_rows']} skipped)"
            )

            # Update header info
            header_info = self.query_one("#info-header", Label)
            if self.file_info['header_detected']:
                header_values = self.file_info.get('header_values', [])
                header_text = f"Header: YES ({', '.join(header_values[:3])}{'...' if len(header_values) > 3 else ''})"
                header_info.update(header_text)
                header_info.remove_class("header-not-detected")
                header_info.add_class("header-detected")
            else:
                header_info.update("Header: NO (auto-detected)")
                header_info.remove_class("header-detected")
                header_info.add_class("header-not-detected")

            # Show what will happen with current header setting
            will_skip = self._will_skip_header()
            if will_skip:
                self.notify(
                    f"File analyzed: {self.file_info['data_rows']} data rows, header will be skipped",
                    severity="information"
                )
            else:
                self.notify(
                    f"File analyzed: {self.file_info['data_rows']} data rows, header will be included",
                    severity="information"
                )

        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            self.notify(f"Error analyzing file: {e}", severity="error")

    def _will_skip_header(self) -> bool:
        """Determine if header will be skipped based on settings."""
        if self.skip_header is True:
            return True
        if self.skip_header is False:
            return False
        if self.skip_header == "auto":
            return self.file_info.get('header_detected', False)
        return False

    @on(Button.Pressed, "#process-btn")
    def on_process_pressed(self) -> None:
        """Handle process button press."""
        if not self.selected_file:
            self.notify("Please select a CSV file first", severity="error")
            return

        # Collect settings from UI
        self._collect_settings()

        # Switch to processing screen with skip_header setting
        from m365_ioc_csv.tui.screens.processing_screen import ProcessingScreen

        processing_screen = ProcessingScreen(
            input_file=self.selected_file,
            settings=self.settings,
            skip_header=self.skip_header
        )
        self.app.push_screen(processing_screen)

    @on(Button.Pressed, "#clear-btn")
    def on_clear_pressed(self) -> None:
        """Handle clear button press."""
        self.selected_file = None
        self.ioc_counts.clear()
        self.file_info.clear()

        # Reset file info display
        self.query_one("#info-file", Label).update("File: -")
        self.query_one("#info-delimiter", Label).update("Delimiter: -")
        self.query_one("#info-encoding", Label).update("Encoding: -")
        self.query_one("#info-rows", Label).update("Total Rows: -")
        self.query_one("#info-header", Label).update("Header: -")

        self._update_summary_table()
        self.notify("Selection cleared", severity="information")

    @on(Button.Pressed, "#exit-btn")
    def on_exit_pressed(self) -> None:
        """Handle exit button press."""
        self.app.exit()

    @on(Button.Pressed, "#refresh-btn")
    def on_refresh_pressed(self) -> None:
        """Handle refresh button press - reload the directory tree."""
        try:
            # Get the current directory tree
            file_tree = self.query_one("#file-tree", DirectoryTree)

            # Save current path for notification
            current_path = str(file_tree.path)

            # Use the built-in reload method
            file_tree.reload()

            self.notify(
                f"Directory refreshed: {current_path}",
                severity="information"
            )
            logger.info(f"Directory tree refreshed: {current_path}")

        except Exception as e:
            logger.error(f"Error refreshing directory: {e}", exc_info=True)
            self.notify(
                f"Error refreshing directory: {e}",
                severity="error"
            )

    def _collect_settings(self) -> None:
        """Collect settings from UI widgets."""
        self.settings.action = self.query_one("#action-select", Select).value
        self.settings.severity = self.query_one("#severity-select", Select).value
        self.settings.custom_title = self.query_one("#custom-title", Input).value
        self.settings.custom_description = self.query_one("#custom-description", Input).value
        self.settings.generate_alert = self.query_one("#alert-select", Select).value == "true"
        # Note: Output mode is now always "separate" - removed from UI

        # Handle expiration
        expiration = self.query_one("#expiration-select", Select).value
        if expiration == "never":
            self.settings.expiration_time = ""
        else:
            self.settings.default_expiration_days = int(expiration)

        logger.debug(f"Settings collected: {self.settings.to_dict()}")

    def _update_summary_table(self) -> None:
        """Update the summary table with current IoC counts."""
        table = self.query_one("#summary-table", DataTable)
        table.clear()

        if not self.ioc_counts:
            table.add_row("Selected File", self.selected_file.name if self.selected_file else "-")
            table.add_row("Total IoCs", "0")
            table.add_row("FileSha256", "0")
            table.add_row("FileSha1", "0")
            table.add_row("FileMd5", "0")
            table.add_row("IpAddress", "0")
            table.add_row("DomainName", "0")
            table.add_row("Url", "0")
        else:
            total = sum(self.ioc_counts.values())
            table.add_row("Selected File", self.selected_file.name if self.selected_file else "-")
            table.add_row("Total IoCs", str(total))

            for ioc_type in ["FileSha256", "FileSha1", "FileMd5", "IpAddress", "DomainName", "Url"]:
                count = self.ioc_counts.get(ioc_type, 0)
                table.add_row(ioc_type, str(count))

    def update_ioc_counts(self, counts: dict[str, int]) -> None:
        """Update IoC counts from processing result."""
        self.ioc_counts = counts
        self._update_summary_table()
