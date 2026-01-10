"""
Main entry point for M365 IOC CSV Generator.

This module provides the command-line interface for the application.
Run with: python -m m365_ioc_csv
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is in path for development
_src_path = Path(__file__).parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from m365_ioc_csv.app import IOCApp
from m365_ioc_csv.utils.error_handler import (
    ErrorHandler,
    ExitCode,
    get_error_handler
)
from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> ExitCode:
    """
    Main entry point with comprehensive error handling.

    This function:
    1. Validates the runtime environment
    2. Creates and configures the application
    3. Runs the Textual TUI
    4. Handles any errors gracefully

    Returns:
        Exit code for the application
    """
    handler = get_error_handler()
    handler.logger.info("=" * 60)
    handler.logger.info("M365 IOC CSV Generator v2.0.0 - Starting")
    handler.logger.info("=" * 60)

    try:
        # Validate environment
        _validate_environment()

        # Create and run application
        app = IOCApp()
        exit_code = app.run()

        handler.logger.info(f"Application exited with code: {exit_code.value}")
        return exit_code

    except KeyboardInterrupt:
        handler.logger.info("Application cancelled by user (KeyboardInterrupt)")
        handler.console.print("\n[yellow][CANCELLED] Operation cancelled by user[/yellow]")
        return ExitCode.SUCCESS

    except Exception as e:
        exit_code = handler.handle_exception(e, "main")
        return exit_code


def _validate_environment() -> None:
    """
    Validate runtime environment before starting application.

    Checks:
    - Python version (>= 3.10)
    - Required directories (input, output, logs)
    - Basic filesystem permissions

    Raises:
        DependencyError: If environment requirements are not met
        FileError: If directory validation fails
    """
    from m365_ioc_csv.utils.error_handler import DependencyError

    handler = get_error_handler()

    # Check Python version
    if sys.version_info < (3, 10):
        current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        required = "3.10"
        raise DependencyError(
            f"Python {required}+ required, found {current}",
            dependency=f"Python >={required}"
        )

    handler.logger.debug(f"Python version validated: {sys.version}")

    # Create default directories
    handler.logger.debug("Validating directories...")
    handler.validate_directory(Path("input"), create=True)
    handler.validate_directory(Path("output"), create=True)
    handler.validate_directory(Path("logs"), create=True)

    handler.logger.debug("Environment validation complete")


if __name__ == "__main__":
    # Run the application
    exit_code = main()

    # Exit with proper code
    sys.exit(exit_code.value)
