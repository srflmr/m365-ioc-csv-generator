"""
Comprehensive Error Handling for M365 IOC CSV Generator.

Implements best practices from 2025 industry standards:
- DataCamp: Python Try-Except Tutorial (Aug 2025)
- Qodo AI: 6 Best Practices for Exception Handling (Dec 2024)
- Python Logging Best Practices (2026)
"""

from __future__ import annotations

import csv
import logging
import os
import sys
from datetime import datetime
from enum import Enum, unique
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.traceback import install as install_rich_traceback

# Configure Rich traceback for beautiful error output
install_rich_traceback(show_locals=True, max_frames=10)


@unique
class ExitCode(Enum):
    """Standard exit codes for the application following Unix conventions."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    FILE_NOT_FOUND = 2
    PERMISSION_ERROR = 3
    CSV_PARSE_ERROR = 4
    INVALID_INPUT = 5
    DEPENDENCY_ERROR = 6
    VALIDATION_ERROR = 7
    OUT_OF_MEMORY = 8


class AppError(Exception):
    """
    Base exception for application errors.

    Attributes:
        message: Human-readable error message
        exit_code: Exit code for the application
        details: Additional error details (optional)
    """

    def __init__(self, message: str, exit_code: ExitCode = ExitCode.GENERAL_ERROR,
                 details: Optional[str] = None) -> None:
        self.message = message
        self.exit_code = exit_code
        self.details = details
        super().__init__(self.message)


class FileError(AppError):
    """File-related errors (not found, permission, etc.)."""

    def __init__(self, message: str, file_path: Optional[Path] = None,
                 exit_code: ExitCode = ExitCode.FILE_NOT_FOUND) -> None:
        details = f"File: {file_path}" if file_path else None
        super().__init__(message, exit_code, details)


class CSVError(AppError):
    """CSV parsing and validation errors."""

    def __init__(self, message: str, line_number: Optional[int] = None,
                 exit_code: ExitCode = ExitCode.CSV_PARSE_ERROR) -> None:
        details = f"Line: {line_number}" if line_number is not None else None
        super().__init__(message, exit_code, details)


class ValidationError(AppError):
    """Input validation errors."""

    def __init__(self, message: str, field: Optional[str] = None,
                 exit_code: ExitCode = ExitCode.VALIDATION_ERROR) -> None:
        details = f"Field: {field}" if field else None
        super().__init__(message, exit_code, details)


class DependencyError(AppError):
    """Dependency-related errors."""

    def __init__(self, message: str, dependency: Optional[str] = None) -> None:
        details = f"Dependency: {dependency}" if dependency else None
        super().__init__(message, ExitCode.DEPENDENCY_ERROR, details)


class ErrorHandler:
    """
    Centralized error handling with logging and user-friendly messages.

    Features:
    - Structured logging with file rotation
    - User-friendly error messages
    - Detailed logging for debugging
    - Hints for common errors
    - Cross-platform path handling

    Example:
        handler = ErrorHandler()
        try:
            process_csv(file_path)
        except Exception as e:
            exit_code = handler.handle_exception(e, "process_csv")
            sys.exit(exit_code.value)
    """

    def __init__(self, log_dir: Path = Path("logs"), app_name: str = "M365_IOC_CSV") -> None:
        """
        Initialize the error handler.

        Args:
            log_dir: Directory for log files (created if doesn't exist)
            app_name: Application name for log files
        """
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Console for rich output
        self.console = Console()

        self.logger.info(f"ErrorHandler initialized for {app_name}")

    def _setup_logging(self) -> None:
        """Configure logging with file rotation and structured format."""
        log_file = self.log_dir / f"{self.app_name}_{datetime.now():%Y%m%d}.log"

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)-8s %(message)s'
        )

        # File handler with rotation (5MB max, keep 3 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)

        # Console handler (less verbose)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()  # Remove existing handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Create module logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Logging configured. Log file: {log_file}")

    def handle_exception(
        self,
        exc: Exception,
        context: str = "",
        show_traceback: bool = False
    ) -> ExitCode:
        """
        Handle exception with logging and user-friendly message.

        Args:
            exc: The exception to handle
            context: Additional context about where error occurred
            show_traceback: Whether to show full traceback to user

        Returns:
            Exit code for the application
        """
        # Log the exception with full traceback
        context_str = f" in {context}" if context else ""
        self.logger.error(
            f"Exception{context_str}: {type(exc).__name__}: {exc}",
            exc_info=True
        )

        # Determine exit code and user message
        exit_code, user_message = self._classify_exception(exc)

        # Show user-friendly message
        self._show_error_message(user_message, exit_code, exc, show_traceback)

        # Log hints
        self._log_hints(exit_code)

        return exit_code

    def _classify_exception(self, exc: Exception) -> tuple[ExitCode, str]:
        """Classify exception and return exit code with user message."""
        if isinstance(exc, AppError):
            return exc.exit_code, exc.message

        # Built-in exceptions
        if isinstance(exc, FileNotFoundError):
            return ExitCode.FILE_NOT_FOUND, f"File not found: {exc.filename}"
        if isinstance(exc, PermissionError):
            return ExitCode.PERMISSION_ERROR, f"Permission denied: {exc.filename}"
        if isinstance(exc, (csv.Error, ValueError)):
            return ExitCode.CSV_PARSE_ERROR, f"Failed to parse CSV: {exc}"
        if isinstance(exc, MemoryError):
            return ExitCode.OUT_OF_MEMORY, "Out of memory. Try processing a smaller file."
        if isinstance(exc, (KeyboardInterrupt,)):
            return ExitCode.SUCCESS, "Operation cancelled by user"

        # Default
        return ExitCode.GENERAL_ERROR, f"An unexpected error occurred: {exc}"

    def _show_error_message(
        self,
        message: str,
        exit_code: ExitCode,
        exc: Exception,
        show_traceback: bool
    ) -> None:
        """Display user-friendly error message."""
        self.console.print(f"\n[red][ERROR] {message}[/red]\n")

        # Show details if available
        if isinstance(exc, AppError) and exc.details:
            self.console.print(f"[dim]Details: {exc.details}[/dim]\n")

        # Show traceback if requested
        if show_traceback:
            self.console.print_exception()

        # Show log file location
        log_file = self.log_dir / f"{self.app_name}_{datetime.now():%Y%m%d}.log"
        self.console.print(f"\n[dim]Log file: {log_file}[/dim]")

    def _log_hints(self, exit_code: ExitCode) -> None:
        """Log hints for common errors."""
        hints = {
            ExitCode.FILE_NOT_FOUND: [
                "Check that the file path is correct",
                "Use the file explorer to browse available files",
                "Ensure the file exists in the input directory"
            ],
            ExitCode.CSV_PARSE_ERROR: [
                "Ensure the CSV file is properly formatted",
                "Check that the delimiter is consistent (comma, semicolon, tab)",
                "Verify all quoted values are properly closed",
                "Check for special characters that need escaping"
            ],
            ExitCode.PERMISSION_ERROR: [
                "Check file and directory permissions",
                "Ensure you have read access to the input file",
                "Ensure you have write access to the output directory",
                "Try running with appropriate privileges"
            ],
            ExitCode.VALIDATION_ERROR: [
                "Check that all required fields are filled",
                "Verify the values are in the correct format",
                "Refer to the help text for field requirements"
            ],
            ExitCode.DEPENDENCY_ERROR: [
                "Run the setup script to install dependencies",
                "Check your internet connection",
                "Try: pip install -e ."
            ]
        }

        if exit_code in hints:
            self.logger.debug("Hints for %s: %s", exit_code, hints[exit_code])
            self.console.print("\n[yellow]Suggestions:[/yellow]")
            for hint in hints[exit_code]:
                self.console.print(f"  [dim]• {hint}[/dim]")
            self.console.print("")

    def validate_file(self, file_path: Path, must_exist: bool = True) -> None:
        """
        Validate file exists and is accessible.

        Args:
            file_path: Path to validate
            must_exist: Whether the file must exist

        Raises:
            FileError: If validation fails
        """
        self.logger.debug(f"Validating file: {file_path}")

        if must_exist and not file_path.exists():
            raise FileError(
                f"File not found: {file_path}",
                file_path=file_path
            )

        if file_path.exists() and not file_path.is_file():
            raise FileError(
                f"Not a file: {file_path}",
                file_path=file_path,
                exit_code=ExitCode.INVALID_INPUT
            )

        if file_path.exists():
            if not os.access(file_path, os.R_OK):
                raise FileError(
                    f"File is not readable: {file_path}",
                    file_path=file_path,
                    exit_code=ExitCode.PERMISSION_ERROR
                )
            self.logger.debug(f"File validation passed: {file_path}")

    def validate_directory(
        self,
        dir_path: Path,
        create: bool = False,
        writable: bool = False
    ) -> None:
        """
        Validate directory exists and is accessible.

        Args:
            dir_path: Directory path to validate
            create: Whether to create the directory if it doesn't exist
            writable: Whether the directory must be writable

        Raises:
            FileError: If validation fails
        """
        self.logger.debug(f"Validating directory: {dir_path}")

        if not dir_path.exists():
            if create:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.logger.debug(f"Created directory: {dir_path}")
                except OSError as e:
                    raise FileError(
                        f"Cannot create directory: {dir_path}",
                        file_path=dir_path,
                        exit_code=ExitCode.PERMISSION_ERROR
                    )
            else:
                raise FileError(
                    f"Directory not found: {dir_path}",
                    file_path=dir_path
                )

        if dir_path.exists() and not dir_path.is_dir():
            raise FileError(
                f"Not a directory: {dir_path}",
                file_path=dir_path,
                exit_code=ExitCode.INVALID_INPUT
            )

        if writable and dir_path.exists():
            if not os.access(dir_path, os.W_OK):
                raise FileError(
                    f"Directory is not writable: {dir_path}",
                    file_path=dir_path,
                    exit_code=ExitCode.PERMISSION_ERROR
                )

        self.logger.debug(f"Directory validation passed: {dir_path}")

    def validate_python_version(self, min_version: tuple[int, int] = (3, 10)) -> None:
        """
        Validate Python version meets minimum requirement.

        Args:
            min_version: Minimum required version as (major, minor)

        Raises:
            DependencyError: If Python version is too old
        """
        if sys.version_info < min_version:
            current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            required = f"{min_version[0]}.{min_version[1]}"
            raise DependencyError(
                f"Python {required}+ required, found {current}",
                dependency=f"Python >={required}"
            )
        self.logger.debug(f"Python version validated: {sys.version}")


# Global error handler instance (lazy initialization)
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def safe_execute(func, *args: Any, default: Any = None, **kwargs: Any) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default: Default value to return on error
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default value on error

    Example:
        result = safe_execute(int, "123", default=0)
        # Returns: 123

        result = safe_execute(int, "abc", default=0)
        # Returns: 0 (error logged)
    """
    handler = get_error_handler()
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler.logger.warning(f"safe_execute failed for {func.__name__}: {e}")
        return default


def validate_ioc_value(value: str, ioc_type: str) -> None:
    """
    Validate an IoC value based on its type.

    Args:
        value: The IoC value to validate
        ioc_type: The type of IoC (FileSha256, FileSha1, IpAddress, DomainName, Url)

    Raises:
        ValidationError: If validation fails
    """
    from m365_ioc_csv.core.ioc_detector import IoCDetector

    detector = IoCDetector()
    detected = detector.detect_type(value)

    if detected != ioc_type:
        raise ValidationError(
            f"Value '{value}' is not a valid {ioc_type}",
            field=ioc_type
        )
