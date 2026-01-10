"""
CSV Writer Module for Microsoft 365 Defender Bulk Import.

Generates CSV files in the format required by Microsoft Defender for bulk IoC import.

CSV Format (following Microsoft Defender sample):
IndicatorType,IndicatorValue,ExpirationTime,Action,Severity,Title,Description,
RecommendedActions,RbacGroups,Category,MitreTechniques,GenerateAlert

Features:
- One CSV per IoC type
- Auto-split files > 500 rows (Microsoft best practice)
- Custom naming with timestamp and metadata
- Proper CSV escaping for special characters
"""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from enum import Enum, unique
from pathlib import Path
from typing import Optional, Any

from m365_ioc_csv.core.ioc_detector import IoCType
from m365_ioc_csv.core.config import Settings
from m365_ioc_csv.utils.error_handler import FileError, get_error_handler
from m365_ioc_csv.utils.logger import get_logger, ProcessingLogger

logger = get_logger(__name__)


# CSV header matching Microsoft Defender format
CSV_HEADER = [
    "IndicatorType",
    "IndicatorValue",
    "ExpirationTime",
    "Action",
    "Severity",
    "Title",
    "Description",
    "RecommendedActions",
    "RbacGroups",
    "Category",
    "MitreTechniques",
    "GenerateAlert",
]

# Default recommended actions per IoC type
DEFAULT_RECOMMENDED = {
    IoCType.FILE_SHA256: "Block execution",
    IoCType.FILE_SHA1: "Block execution",
    IoCType.IP_ADDRESS: "Block network connection",
    IoCType.DOMAIN_NAME: "Block domain",
    IoCType.URL: "Block URL",
}

# Default category per IoC type (based on MITRE ATT&CK)
DEFAULT_CATEGORY = {
    IoCType.FILE_SHA256: "Execution",
    IoCType.FILE_SHA1: "Execution",
    IoCType.IP_ADDRESS: "InitialAccess",
    IoCType.DOMAIN_NAME: "CommandAndControl",
    IoCType.URL: "InitialAccess",
}

# Maximum rows per CSV file (Microsoft best practice)
MAX_ROWS_PER_FILE = 500


@unique
class OutputMode(Enum):
    """Output mode for generated files."""

    SEPARATE = "separate"  # One CSV per IoC type
    COMBINED = "combined"  # Single CSV with all types
    BOTH = "both"  # Both separate and combined


@dataclass
class IoCRow:
    """
    Represents a single row in the output CSV.

    Attributes:
        ioc_type: Type of indicator (e.g., FileSha256, IpAddress)
        value: The indicator value itself
        expiration_time: When the indicator expires (empty = never)
        action: Action to take (Block, Audit, Warn, Allowed, BlockAndRemediate)
        severity: Severity level (Informational, Low, Medium, High)
        title: Custom title for the indicator
        description: Custom description
        recommended_actions: Recommended remediation steps
        rbac_groups: RBAC group names (semicolon-separated)
        category: Threat category
        mitre_techniques: MITRE ATT&CK techniques (comma-separated)
        generate_alert: Whether to generate an alert ("true" or "false")
    """

    ioc_type: str
    value: str
    expiration_time: str
    action: str
    severity: str
    title: str
    description: str
    recommended_actions: str
    rbac_groups: str
    category: str
    mitre_techniques: str
    generate_alert: str

    def to_list(self) -> list[str]:
        """Convert row to list for CSV writing."""
        return [
            self.ioc_type,
            self.value,
            self.expiration_time,
            self.action,
            self.severity,
            self.title,
            self.description,
            self.recommended_actions,
            self.rbac_groups,
            self.category,
            self.mitre_techniques,
            self.generate_alert,
        ]


@dataclass
class WriteResult:
    """
    Result of CSV writing operation.

    Attributes:
        files_written: List of paths to written files
        total_rows: Total number of rows written
        total_files: Total number of files created
        ioc_counts: Dictionary of IoC type counts
    """

    files_written: list[Path] = field(default_factory=list)
    total_rows: int = 0
    total_files: int = 0
    ioc_counts: dict[str, int] = field(default_factory=dict)


class CSVWriter:
    """
    Write Microsoft 365 Defender compatible CSV files.

    Features:
    - Proper CSV formatting with escaping
    - Auto-split files > 500 rows
    - Custom naming with timestamp
    - Creates output directory if needed
    - Progress tracking

    Example:
        writer = CSVWriter(settings)
        result = writer.write_iocs(ioc_dict, output_dir)
        print(f"Wrote {result.total_rows} rows to {result.total_files} files")
    """

    def __init__(
        self,
        settings: Settings,
        max_rows_per_file: int = MAX_ROWS_PER_FILE,
        file_prefix: Optional[str] = None
    ) -> None:
        """
        Initialize CSV writer.

        Args:
            settings: Application settings for row generation
            max_rows_per_file: Maximum rows per output file
            file_prefix: Optional custom prefix for output files
        """
        self.settings = settings
        self.max_rows_per_file = max_rows_per_file
        self.file_prefix = file_prefix
        self.error_handler = get_error_handler()
        logger.debug(f"CSVWriter initialized with max_rows={max_rows_per_file}")

    def write_iocs(
        self,
        ioc_dict: dict[str, list[str]],
        output_dir: Path,
        mode: OutputMode = OutputMode.SEPARATE,
        source_file: str = "import"
    ) -> WriteResult:
        """
        Write IoCs to CSV file(s).

        Args:
            ioc_dict: Dictionary mapping IoC types to lists of values
            output_dir: Directory to write output files
            mode: Output mode (separate, combined, or both)
            source_file: Name of source file (for description)

        Returns:
            WriteResult with information about written files
        """
        proc_log = ProcessingLogger("CSV Writing")
        proc_log.start(f"Writing IoCs to {output_dir}")

        # Ensure output directory exists
        self.error_handler.validate_directory(output_dir, create=True, writable=True)

        result = WriteResult()

        # Get timestamp for filenames
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate rows for each IoC type
        rows_by_type: dict[str, list[list[str]]] = {}
        for ioc_type, values in ioc_dict.items():
            if not values:
                continue

            rows = [self._create_row(ioc_type, value, source_file) for value in values]
            rows_by_type[ioc_type] = rows
            result.ioc_counts[ioc_type] = len(values)

        # Write separate CSVs (one per type)
        if mode in (OutputMode.SEPARATE, OutputMode.BOTH):
            for ioc_type, rows in rows_by_type.items():
                files = self._write_csv_files(
                    rows,
                    output_dir,
                    f"{timestamp}_{ioc_type}_{self.settings.action}",
                    "separate"
                )
                result.files_written.extend(files)

        # Write combined CSV (all types)
        if mode in (OutputMode.COMBINED, OutputMode.BOTH):
            combined_rows = []
            for rows in rows_by_type.values():
                combined_rows.extend(rows)

            if combined_rows:
                files = self._write_csv_files(
                    combined_rows,
                    output_dir,
                    f"{timestamp}_AllTypes_{self.settings.action}",
                    "combined"
                )
                result.files_written.extend(files)

        # Calculate totals
        result.total_files = len(result.files_written)
        result.total_rows = sum(result.ioc_counts.values())

        proc_log.complete(f"Wrote {result.total_rows} rows to {result.total_files} files")
        return result

    def _create_row(self, ioc_type: str, value: str, source_file: str) -> list[str]:
        """
        Create a CSV row from IoC value.

        Args:
            ioc_type: Type of IoC
            value: IoC value
            source_file: Source file name for description

        Returns:
            List of field values
        """
        # Get defaults based on IoC type
        ioc_type_enum = IoCType(ioc_type) if ioc_type in IoCType._value2member_map_ else None
        recommended = DEFAULT_RECOMMENDED.get(ioc_type_enum, "")
        category = DEFAULT_CATEGORY.get(ioc_type_enum, "SuspiciousActivity")

        # Build title
        title = self.settings.custom_title or f"{self.settings.action.upper()} - {ioc_type}"

        # Build description
        description = self.settings.custom_description or f"Imported via M365 IOC Generator from {source_file}"

        # Create row
        return [
            ioc_type,
            value,
            self.settings.expiration_time,
            self.settings.action,
            self.settings.severity,
            title,
            description,
            recommended,
            self.settings.rbac_groups,
            category,
            self.settings.mitre_techniques,
            "true" if self.settings.generate_alert else "false",
        ]

    def _write_csv_files(
        self,
        rows: list[list[str]],
        output_dir: Path,
        base_name: str,
        file_type: str
    ) -> list[Path]:
        """
        Write CSV file(s), splitting if necessary.

        Args:
            rows: List of CSV rows (excluding header)
            output_dir: Directory to write to
            base_name: Base name for output files
            file_type: Type of file (for logging)

        Returns:
            List of paths to written files
        """
        files_written: list[Path] = []

        # Split into chunks if needed
        chunks = self._chunk_rows(rows, self.max_rows_per_file)

        for idx, chunk in enumerate(chunks, start=1):
            # Add part suffix if multiple chunks
            suffix = f"_part{idx}" if len(chunks) > 1 else ""
            filename = f"{base_name}{suffix}.csv"
            file_path = output_dir / filename

            # Write the file
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(CSV_HEADER)
                    writer.writerows(chunk)

                files_written.append(file_path)
                logger.info(f"Wrote {len(chunk)} rows to {file_path.name}")

            except IOError as e:
                raise FileError(
                    f"Failed to write CSV file: {file_path}",
                    file_path=file_path
                )

        return files_written

    @staticmethod
    def _chunk_rows(rows: list[list[str]], chunk_size: int) -> list[list[list[str]]]:
        """
        Split rows into chunks.

        Args:
            rows: List of rows to split
            chunk_size: Maximum size of each chunk

        Returns:
            List of row chunks
        """
        chunks = []
        for i in range(0, len(rows), chunk_size):
            chunks.append(rows[i:i + chunk_size])
        return chunks

    def write_unknown_iocs(
        self,
        unknown_values: list[str],
        output_dir: Path,
        timestamp: Optional[str] = None
    ) -> Optional[Path]:
        """
        Write unknown/unparsed IoCs to a text file for review.

        Args:
            unknown_values: List of unknown IoC values
            output_dir: Directory to write to
            timestamp: Optional timestamp for filename

        Returns:
            Path to written file, or None if no unknown values
        """
        if not unknown_values:
            return None

        self.error_handler.validate_directory(output_dir, create=True, writable=True)

        if timestamp is None:
            timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

        file_path = output_dir / f"{timestamp}_UNKNOWN.txt"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for value in unknown_values:
                    f.write(value + "\n")

            logger.info(f"Wrote {len(unknown_values)} unknown values to {file_path.name}")
            return file_path

        except IOError as e:
            raise FileError(
                f"Failed to write unknown values file: {file_path}",
                file_path=file_path
            )

    @staticmethod
    def get_csv_header() -> list[str]:
        """Get the CSV header for Microsoft Defender format."""
        return CSV_HEADER.copy()

    @staticmethod
    def get_default_recommended_actions() -> dict[str, str]:
        """Get default recommended actions per IoC type."""
        return {k.value: v for k, v in DEFAULT_RECOMMENDED.items()}

    @staticmethod
    def get_default_categories() -> dict[str, str]:
        """Get default categories per IoC type."""
        return {k.value: v for k, v in DEFAULT_CATEGORY.items()}
