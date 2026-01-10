"""
M365 IOC CSV Generator

Interactive CLI tool to generate Microsoft 365 Defender bulk import CSV files
from a list of Indicators of Compromise (IoCs).

Version: 2.0.0
"""

from __future__ import annotations

__version__ = "2.0.0"
__author__ = "M365 IOC CSV Generator Team"
__license__ = "MIT"

# Public API
from m365_ioc_csv.core.config import Settings, get_app_config
from m365_ioc_csv.core.ioc_detector import IoCDetector, IoCType
from m365_ioc_csv.core.csv_parser import CSVParser
from m365_ioc_csv.core.csv_writer import CSVWriter, OutputMode

__all__ = [
    "Settings",
    "get_app_config",
    "IoCDetector",
    "IoCType",
    "CSVParser",
    "CSVWriter",
    "OutputMode",
]
