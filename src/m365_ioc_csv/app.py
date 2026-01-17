"""
Main application class for M365 IOC CSV Generator.

Built with Textual framework for a modern, responsive TUI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from m365_ioc_csv.core.config import get_app_config
from m365_ioc_csv.utils.error_handler import ErrorHandler, ExitCode
from m365_ioc_csv.utils.logger import get_logger
from m365_ioc_csv.tui.screens.main_screen import MainScreen
from m365_ioc_csv.tui.screens.sheet_selection_screen import SheetSelectionScreen
from m365_ioc_csv.tui.styles import APP_STYLES

logger = get_logger(__name__)


class IOCApp(App):
    """
    Main application for M365 IOC CSV Generator.

    Features:
    - Responsive TUI with Textual
    - File browser for CSV selection
    - Configuration panel
    - Real-time processing feedback
    - Cross-platform support

    Usage:
        app = IOCApp()
        app.run()
    """

    # App configuration
    TITLE = "M365 IOC CSV Generator"
    CSS_PATH = None  # We'll inject styles directly
    CSS = APP_STYLES  # Modern 2026 theme
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    # Register screens as class attribute
    SCREENS = {
        "main": MainScreen,
        "sheet_selection": SheetSelectionScreen,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the application."""
        super().__init__(*args, **kwargs)
        self.app_config = get_app_config()
        self.error_handler = ErrorHandler()

        logger.info(f"{self.TITLE} v{self.app_config.version} initialized")

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when the application is mounted."""
        # Push main screen
        self.push_screen("main")

        logger.info("Application mounted successfully")

    def run(self, *, headless: bool = False) -> ExitCode:
        """
        Run the application.

        Args:
            headless: Run in headless mode (for testing)

        Returns:
            Exit code
        """
        try:
            logger.info("Starting application...")
            super().run(headless=headless)
            return ExitCode.SUCCESS
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            return ExitCode.SUCCESS
        except Exception as e:
            self.error_handler.handle_exception(e, "app.run")
            return ExitCode.GENERAL_ERROR


def create_app() -> IOCApp:
    """
    Create and configure the application instance.

    Returns:
        Configured IOCApp instance
    """
    return IOCApp()
