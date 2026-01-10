"""
Structured logging utilities for M365 IOC CSV Generator.

Provides specialized loggers for different components with consistent formatting.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def get_logger(name: str, log_dir: Optional[Path] = None) -> logging.Logger:
    """
    Get a logger with consistent configuration.

    Args:
        name: Logger name (typically __name__ of the module)
        log_dir: Optional log directory for file handler

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


class ProcessingLogger:
    """
    Specialized logger for processing operations with progress tracking.

    Example:
        proc_log = ProcessingLogger("CSV Processing")
        proc_log.start("Processing CSV file")
        proc_log.progress("Processed 100 rows")
        proc_log.complete("Processing finished")
    """

    def __init__(self, operation: str) -> None:
        """
        Initialize processing logger.

        Args:
            operation: Name of the operation being logged
        """
        self.operation = operation
        self.logger = get_logger(f"processing.{operation}")
        self._start_time: Optional[float] = None

    def start(self, message: str = "") -> None:
        """Log operation start."""
        import time
        self._start_time = time.time()
        msg = message or f"Starting {self.operation}"
        self.logger.info(f"[START] {msg}")

    def progress(self, message: str) -> None:
        """Log progress update."""
        self.logger.info(f"[PROGRESS] {message}")

    def complete(self, message: str = "") -> None:
        """Log operation completion with duration."""
        import time
        duration = ""
        if self._start_time:
            elapsed = time.time() - self._start_time
            duration = f" ({elapsed:.2f}s)"

        msg = message or f"{self.operation} completed"
        self.logger.info(f"[COMPLETE] {msg}{duration}")

    def error(self, message: str) -> None:
        """Log operation error."""
        self.logger.error(f"[ERROR] {message}")

    def warning(self, message: str) -> None:
        """Log operation warning."""
        self.logger.warning(f"[WARNING] {message}")
