"""
Sheet Selection Screen for Excel multi-sheet support.

Allows users to select which sheets to process from an Excel workbook.
Displays sheet metadata (name, row count, estimated IoC count).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Label,
    Static,
)

from m365_ioc_csv.core.excel_parser import ExcelParser, ExcelSheetInfo
from m365_ioc_csv.core.config import Settings
from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


class SheetSelectionScreen(Screen):
    """
    Screen for selecting sheets from Excel workbook.

    Features:
    - DataTable with sheet information
    - Checkbox per sheet for selection
    - Select All / Deselect All buttons
    - Process Selected button
    - Back button to return to file browser
    """

    CSS = """
    SheetSelectionScreen {
        layout: vertical;
    }

    #header-container {
        height: 15%;
        padding: 1 2;
        content-align: center middle;
    }

    #table-container {
        height: 60%;
        border: thick $primary;
        border-title-color: $accent;
        border-title-style: bold;
    }

    #action-container {
        height: 15%;
        align: center middle;
        layout: grid;
        grid-size: 4;
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-gutter: 1;
        padding: 1 0;
    }

    #footer-container {
        height: 10%;
        align: center middle;
    }

    DataTable {
        height: 1fr;
    }

    Button {
        min-width: 15;
        height: 3;
        margin: 0;
    }

    .header-text {
        text-style: bold;
        color: $accent;
        text-align: center;
    }

    .info-text {
        color: $text-muted;
        text-align: center;
    }

    .selected-count {
        text-style: bold;
        color: $success;
    }
    """

    def __init__(
        self,
        excel_file: Path,
        sheets: list[ExcelSheetInfo],
        settings: Settings,
        skip_header: str | bool = "auto",
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Initialize sheet selection screen.

        Args:
            excel_file: Path to the Excel file
            sheets: List of ExcelSheetInfo objects
            settings: Application settings
            skip_header: Whether to skip header row
        """
        super().__init__(*args, **kwargs)
        self.excel_file = excel_file
        self.sheets = sheets
        self.settings = settings
        self.skip_header = skip_header
        self.selected_sheets: set[str] = set()

        # Auto-select all sheets by default
        self.selected_sheets = {sheet.name for sheet in sheets}

        logger.info(
            f"SheetSelectionScreen initialized for {excel_file.name} "
            f"with {len(sheets)} sheets"
        )

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        # Header with file info
        with Container(id="header-container"):
            yield Label(
                f"📊 Select Sheets to Process",
                classes="header-text",
                id="header-title"
            )
            yield Label(
                f"File: {self.excel_file.name}",
                classes="info-text",
                id="file-name"
            )
            yield Label(
                f"Selected: ",
                classes="info-text",
                id="selected-label"
            )
            yield Label(
                f"{len(self.selected_sheets)} of {len(self.sheets)} sheets",
                classes="selected-count",
                id="selected-count"
            )

        # DataTable with sheet info
        with Container(id="table-container"):
            yield DataTable(id="sheets-table")

        # Action buttons
        with Container(id="action-container"):
            yield Button("✓ Select All", id="select-all-btn", variant="default")
            yield Button("✗ Deselect All", id="deselect-all-btn", variant="default")
            yield Button("▶ Process Selected", id="process-btn", variant="primary")
            yield Button("← Back", id="back-btn", variant="default")

        # Footer info
        with Container(id="footer-container"):
            yield Label(
                f"[SPACE] Toggle selection | [ENTER] Process | [ESC] Back",
                classes="info-text"
            )

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Setup DataTable
        table = self.query_one("#sheets-table", DataTable)

        # Add columns
        table.add_column("Select", width=8)
        table.add_column("Sheet Name", width=40)
        table.add_column("Rows", width=10)
        table.add_column("Est. IoCs", width=12)

        # Add rows for each sheet
        for sheet in self.sheets:
            checked = "✓" if sheet.name in self.selected_sheets else "✗"
            row_key = table.add_row(
                checked,
                sheet.name,
                str(sheet.row_count),
                str(sheet.ioc_count),
                key=sheet.name
            )

        logger.info(f"DataTable populated with {len(self.sheets)} sheets")

    @on(DataTable.RowSelected, "#sheets-table")
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (toggle checkbox)."""
        table = self.query_one("#sheets-table", DataTable)
        row_key = event.row_key

        # Get sheet name from row key
        if row_key and row_key in self.selected_sheets:
            # Deselect
            self.selected_sheets.discard(row_key)
            table.update_cell(row_key, "Select", "✗")
        elif row_key:
            # Select
            self.selected_sheets.add(row_key)
            table.update_cell(row_key, "Select", "✓")

        # Update count display
        self._update_selected_count()

        logger.debug(f"Sheet selection changed: {len(self.selected_sheets)} selected")

    @on(Button.Pressed, "#select-all-btn")
    def on_select_all_pressed(self) -> None:
        """Handle Select All button press."""
        table = self.query_one("#sheets-table", DataTable)

        for sheet in self.sheets:
            self.selected_sheets.add(sheet.name)
            table.update_cell(sheet.name, "Select", "✓")

        self._update_selected_count()
        logger.info("All sheets selected")

    @on(Button.Pressed, "#deselect-all-btn")
    def on_deselect_all_pressed(self) -> None:
        """Handle Deselect All button press."""
        table = self.query_one("#sheets-table", DataTable)

        for sheet in self.sheets:
            self.selected_sheets.discard(sheet.name)
            table.update_cell(sheet.name, "Select", "✗")

        self._update_selected_count()
        logger.info("All sheets deselected")

    @on(Button.Pressed, "#process-btn")
    def on_process_pressed(self) -> None:
        """Handle Process button press."""
        if not self.selected_sheets:
            self.notify(
                "Please select at least one sheet to process",
                severity="error"
            )
            return

        logger.info(f"Processing {len(self.selected_sheets)} selected sheets")

        # Import here to avoid circular dependency
        from m365_ioc_csv.tui.screens.processing_screen import ProcessingScreen

        # Create processing screen with selected sheets
        processing_screen = ProcessingScreen(
            input_file=self.excel_file,
            settings=self.settings,
            skip_header=self.skip_header,
            excel_sheets=list(self.selected_sheets)
        )

        self.app.push_screen(processing_screen)

    @on(Button.Pressed, "#back-btn")
    def on_back_pressed(self) -> None:
        """Handle Back button press."""
        self.app.pop_screen()

    def _update_selected_count(self) -> None:
        """Update the selected count display."""
        count_label = self.query_one("#selected-count", Label)
        count_label.update(f"{len(self.selected_sheets)} of {len(self.sheets)} sheets")

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        # ESC to go back
        if event.key == "escape":
            self.app.pop_screen()
        # ENTER to process
        if event.key == "enter":
            self.on_process_pressed()
