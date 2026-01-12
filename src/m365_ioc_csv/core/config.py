"""
Configuration module for M365 IOC CSV Generator.

Defines settings and configuration options for the application.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum, unique
from pathlib import Path
from typing import Optional

from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


@unique
class Action(Enum):
    """Microsoft Defender indicator actions."""

    BLOCK = "Block"
    AUDIT = "Audit"
    WARN = "Warn"
    ALLOWED = "Allowed"
    BLOCK_AND_REMEDIATE = "BlockAndRemediate"

    def __str__(self) -> str:
        return self.value


@unique
class Severity(Enum):
    """Microsoft Defender severity levels."""

    INFORMATIONAL = "Informational"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    def __str__(self) -> str:
        return self.value


@dataclass
class Settings:
    """
    Application settings for CSV generation.

    Attributes:
        action: Action to take when IoC is detected
        severity: Severity level for the IoC
        expiration_time: When the IoC expires (empty = never expire)
        generate_alert: Whether to generate an alert
        rbac_groups: RBAC group names (semicolon-separated)
        mitre_techniques: MITRE ATT&CK techniques (comma-separated)
        custom_title: Custom title for IoCs (empty = use default)
        custom_description: Custom description for IoCs (empty = use default)
        max_rows_per_file: Maximum rows per output file (default 500)
    """

    # Basic settings
    action: str = Action.BLOCK.value
    severity: str = Severity.HIGH.value

    # Expiration
    expiration_time: str = ""  # Empty = never expire
    default_expiration_days: int = 365  # Days from now for default expiration

    # Alert settings
    generate_alert: bool = True

    # Advanced settings
    rbac_groups: str = ""
    mitre_techniques: str = ""

    # Custom fields
    custom_title: str = ""
    custom_description: str = ""

    # Output settings
    max_rows_per_file: int = 500

    # Directory settings
    input_dir: Path = field(default_factory=lambda: Path("input"))
    output_dir: Path = field(default_factory=lambda: Path("output"))

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        # Convert string paths to Path objects
        if isinstance(self.input_dir, str):
            self.input_dir = Path(self.input_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Validate action
        valid_actions = [a.value for a in Action]
        if self.action not in valid_actions:
            logger.warning(f"Invalid action '{self.action}', using default 'Block'")
            self.action = Action.BLOCK.value

        # Validate severity
        valid_severities = [s.value for s in Severity]
        if self.severity not in valid_severities:
            logger.warning(f"Invalid severity '{self.severity}', using default 'High'")
            self.severity = Severity.HIGH.value

        # Validate max rows
        if self.max_rows_per_file < 1:
            logger.warning("max_rows_per_file must be positive, using default 500")
            self.max_rows_per_file = 500

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create settings from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def save(self, file_path: Path) -> None:
        """
        Save settings to JSON file.

        Args:
            file_path: Path to save settings
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        logger.info(f"Settings saved to {file_path}")

    @classmethod
    def load(cls, file_path: Path) -> "Settings":
        """
        Load settings from JSON file.

        Args:
            file_path: Path to load settings from

        Returns:
            Loaded Settings object
        """
        file_path = Path(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        settings = cls.from_dict(data)
        logger.info(f"Settings loaded from {file_path}")
        return settings

    def get_expiration_string(self, days: Optional[int] = None) -> str:
        """
        Get expiration time string in ISO 8601 format.

        Args:
            days: Days from now (uses default if not specified)

        Returns:
            ISO 8601 formatted datetime string or empty for never expire
        """
        if not self.expiration_time and self.default_expiration_days > 0:
            days = days or self.default_expiration_days
            from datetime import datetime, timedelta
            exp_date = datetime.now() + timedelta(days=days)
            return exp_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        return self.expiration_time

    @staticmethod
    def get_available_actions() -> list[str]:
        """Get list of available actions."""
        return [a.value for a in Action]

    @staticmethod
    def get_available_severities() -> list[str]:
        """Get list of available severities."""
        return [s.value for s in Severity]


@dataclass
class AppConfig:
    """
    Global application configuration.

    Attributes:
        app_name: Application name
        version: Application version
        log_dir: Directory for log files
        config_dir: Directory for configuration files
        max_file_size_mb: Maximum input file size in MB
        supported_extensions: Supported file extensions for input
    """

    app_name: str = "M365 IOC CSV Generator"
    version: str = "2.0.0"
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    config_dir: Path = field(default_factory=lambda: Path("config"))
    max_file_size_mb: int = 100
    supported_extensions: tuple = (".csv", ".tsv", ".txt")

    def __post_init__(self) -> None:
        """Ensure directories are Path objects."""
        if isinstance(self.log_dir, str):
            self.log_dir = Path(self.log_dir)
        if isinstance(self.config_dir, str):
            self.config_dir = Path(self.config_dir)


# Global configuration instance
_app_config: Optional[AppConfig] = None


def get_app_config() -> AppConfig:
    """Get global application configuration."""
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config


def get_default_settings() -> Settings:
    """Get default application settings."""
    return Settings()


def validate_file_size(file_path: Path, max_size_mb: int = 100) -> bool:
    """
    Validate file size is within limits.

    Args:
        file_path: Path to file
        max_size_mb: Maximum size in megabytes

    Returns:
        True if file size is within limits
    """
    if not file_path.exists():
        return False

    size_bytes = file_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > max_size_mb:
        logger.warning(f"File {file_path.name} is too large: {size_mb:.1f}MB")
        return False

    return True
