"""
CSV Parser Module with Automatic Delimiter and Header Detection.

Handles various CSV formats:
- Comma-separated (CSV)
- Semicolon-separated (common in European locales)
- Tab-separated (TSV)
- Pipe-separated
- Auto-detection using csv.Sniffer()
- Smart header detection

Supports:
- Quoted values (single and double quotes)
- Comments (lines starting with #)
- Multiple encodings (UTF-8, Latin-1, etc.)
- Different line endings (CRLF, LF)
- Automatic header row detection and skipping
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass, field
from enum import Enum, unique
from pathlib import Path
from typing import Optional, Generator, Any

from m365_ioc_csv.utils.error_handler import CSVError, FileError
from m365_ioc_csv.utils.error_handler import get_error_handler
from m365_ioc_csv.utils.logger import get_logger, ProcessingLogger

logger = get_logger(__name__)


# Common header keywords for detection
HEADER_KEYWORDS = [
    "indicator", "type", "value", "action", "severity",
    "ip", "domain", "url", "hash", "file", "sha256",
    "sha1", "md5", "threat", "ioc", "address", "host",
    "description", "category", "source", "status"
]


@unique
class CSVDelimiter(Enum):
    """Common CSV delimiters."""

    COMMA = ","
    SEMICOLON = ";"
    TAB = "\t"
    PIPE = "|"
    COLON = ":"

    @classmethod
    def all(cls) -> str:
        """Return string with all delimiters for Sniffer."""
        return ",;\t|:"


@unique
class CSVEncoding(Enum):
    """Common text encodings for CSV files."""

    UTF8 = "utf-8"
    UTF8_SIG = "utf-8-sig"  # UTF-8 with BOM
    LATIN1 = "latin-1"
    CP1252 = "cp1252"
    ISO88591 = "iso-8859-1"


@dataclass
class CSVRow:
    """
    Represents a single row from a CSV file.

    Attributes:
        raw: Original raw line from the file
        values: List of parsed values
        line_number: Line number in the source file (1-indexed)
        is_header: Whether this row was detected as a header
    """

    raw: str
    values: list[str]
    line_number: int
    is_header: bool = False

    @property
    def is_empty(self) -> bool:
        """Check if row is empty (no values or all whitespace)."""
        return not self.values or all(not v.strip() for v in self.values)

    @property
    def is_comment(self) -> bool:
        """Check if row is a comment (starts with #)."""
        return self.raw.strip().startswith("#")


@dataclass
class CSVParseResult:
    """
    Result of parsing a CSV file.

    Attributes:
        rows: List of parsed rows (excluding comments and empty lines)
        ioc_values: Extracted IoC values (all values from all rows)
        delimiter: Detected delimiter
        encoding: Detected encoding
        total_rows: Total number of rows (including comments/empty)
        data_rows: Number of actual data rows (non-header, non-comment)
        skipped_rows: Number of skipped rows (comments/empty/headers)
        header_detected: Whether a header row was detected
        header_row: The detected header row (if any)
        unknown_values: Values that couldn't be classified as IoCs
    """

    rows: list[CSVRow] = field(default_factory=list)
    ioc_values: list[str] = field(default_factory=list)
    delimiter: str = ","
    encoding: str = "utf-8"
    total_rows: int = 0
    data_rows: int = 0
    skipped_rows: int = 0
    header_detected: bool = False
    header_row: Optional[CSVRow] = None
    unknown_values: list[str] = field(default_factory=list)


class CSVParser:
    """
    Parse CSV files with automatic delimiter, encoding, and header detection.

    Features:
    - Automatic delimiter detection using csv.Sniffer()
    - Multiple encoding support with fallback
    - Smart header detection with heuristics
    - User-controllable header skipping
    - Handles quoted values
    - Skips comments and empty lines
    - Extracts all values for IoC detection
    - Memory-efficient streaming for large files

    Example:
        parser = CSVParser()
        result = parser.parse(Path("input.csv"), skip_header="auto")
        for ioc in result.ioc_values:
            print(ioc)
    """

    # Default delimiters to try in order
    DEFAULT_DELIMITERS = [",", ";", "\t", "|"]

    # Default encodings to try in order
    DEFAULT_ENCODINGS = [
        CSVEncoding.UTF8.value,
        CSVEncoding.UTF8_SIG.value,
        CSVEncoding.LATIN1.value,
        CSVEncoding.CP1252.value,
    ]

    def __init__(
        self,
        delimiters: Optional[list[str]] = None,
        encodings: Optional[list[str]] = None
    ) -> None:
        """
        Initialize CSV parser.

        Args:
            delimiters: List of delimiters to try (default: comma, semicolon, tab, pipe)
            encodings: List of encodings to try (default: utf-8 variants)
        """
        self.delimiters = delimiters or self.DEFAULT_DELIMITERS
        self.encodings = encodings or self.DEFAULT_ENCODINGS
        self.error_handler = get_error_handler()
        logger.debug(f"CSVParser initialized with delimiters: {self.delimiters}")

    def parse(
        self,
        file_path: Path,
        skip_header: str | bool = "auto"
    ) -> CSVParseResult:
        """
        Parse a CSV file and extract all values.

        Args:
            file_path: Path to the CSV file
            skip_header: Whether to skip header row
                - True: Always skip first row
                - False: Never skip first row
                - "auto" (default): Auto-detect and skip if header found

        Returns:
            CSVParseResult with extracted data

        Raises:
            FileError: If file cannot be read
            CSVError: If parsing fails
        """
        proc_log = ProcessingLogger("CSV Parsing")
        proc_log.start(f"Parsing file: {file_path.name}")

        # Validate file
        self.error_handler.validate_file(file_path)

        # Detect delimiter and encoding
        delimiter, encoding = self._detect_format(file_path)
        logger.info(f"Detected format: delimiter='{delimiter}', encoding={encoding}")

        # Parse the file
        result = CSVParseResult(delimiter=delimiter, encoding=encoding)

        try:
            with open(file_path, "r", newline="", encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)

                first_row = True
                first_data_row: Optional[CSVRow] = None

                for line_num, raw_row in enumerate(reader, start=1):
                    result.total_rows += 1

                    # Create raw line for reference
                    raw_line = delimiter.join(raw_row) if raw_row else ""

                    # Skip empty lines
                    if not raw_row or all(not cell.strip() for cell in raw_row):
                        result.skipped_rows += 1
                        logger.debug(f"Line {line_num}: Empty line, skipping")
                        continue

                    # Skip comments
                    if raw_line.strip().startswith("#"):
                        result.skipped_rows += 1
                        logger.debug(f"Line {line_num}: Comment, skipping")
                        continue

                    # Create CSV row
                    row = CSVRow(raw=raw_line, values=raw_row, line_number=line_num)

                    # Handle header detection
                    if first_row:
                        first_row = False
                        first_data_row = row

                        # Determine if we should skip this row as header
                        should_skip = self._should_skip_header(row, skip_header)

                        if should_skip:
                            result.header_detected = True
                            result.header_row = row
                            result.skipped_rows += 1
                            logger.info(f"Line {line_num}: Header detected and skipped")
                            logger.debug(f"Header values: {row.values}")
                            continue

                    # Add row to results
                    result.rows.append(row)
                    result.data_rows += 1

                    # Extract all non-empty values
                    for value in raw_row:
                        cleaned = value.strip()
                        if cleaned:
                            # Remove surrounding quotes if present
                            if (cleaned.startswith('"') and cleaned.endswith('"')) or \
                               (cleaned.startswith("'") and cleaned.endswith("'")):
                                cleaned = cleaned[1:-1].strip()

                            if cleaned:
                                result.ioc_values.append(cleaned)

            logger.info(
                f"Parsed {result.total_rows} rows: {result.data_rows} data, "
                f"{result.skipped_rows} skipped (header={result.header_detected})"
            )
            proc_log.complete(
                f"Parsed {result.total_rows} rows, extracted {len(result.ioc_values)} values"
            )
            return result

        except csv.Error as e:
            raise CSVError(f"CSV parsing error: {e}", line_number=line_num)
        except UnicodeDecodeError as e:
            raise CSVError(
                f"Encoding error: {e}. Try saving the file as UTF-8.",
                encoding=encoding
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing CSV: {e}")
            raise CSVError(f"Failed to parse CSV file: {e}")

    def _should_skip_header(self, row: CSVRow, skip_header: str | bool) -> bool:
        """
        Determine if a row should be skipped as a header.

        Args:
            row: The row to check
            skip_header: User preference for header handling

        Returns:
            True if the row should be skipped as a header
        """
        # Explicit True/False from user
        if skip_header is True:
            return True
        if skip_header is False:
            return False

        # Auto-detect mode
        if skip_header == "auto":
            return self._is_likely_header(row)

        return False

    def _is_likely_header(self, row: CSVRow) -> bool:
        """
        Detect if a row is likely a header using heuristics.

        Heuristics:
        1. Contains common header keywords
        2. Has multiple non-IoC values
        3. Values are mostly text (not hashes/IPs/domains)

        Args:
            row: The row to check

        Returns:
            True if the row appears to be a header
        """
        if not row.values:
            return False

        # Combine all values for analysis
        row_text = " ".join(row.values).lower()

        # Check for header keywords
        keyword_count = sum(1 for keyword in HEADER_KEYWORDS if keyword in row_text)

        if keyword_count >= 1:
            # At least one header keyword found
            # Additional check: ensure values don't look like actual IoCs
            ioc_like_count = 0
            for value in row.values:
                if self._looks_like_ioc(value):
                    ioc_like_count += 1

            # If more than half look like IoCs, it's probably not a header
            if ioc_like_count > len(row.values) / 2:
                return False

            logger.debug(
                f"Header detection: {keyword_count} keywords found, "
                f"{ioc_like_count}/{len(row.values)} IoC-like values"
            )
            return True

        return False

    def _looks_like_ioc(self, value: str) -> bool:
        """
        Quick check if a value looks like an IoC.

        Args:
            value: The value to check

        Returns:
            True if the value resembles an IoC
        """
        value = value.strip().lower()

        # IPv4 pattern
        if self._is_ipv4_pattern(value):
            return True

        # Domain pattern
        if "." in value and not value.startswith("http"):
            # Check for typical domain structure
            parts = value.split(".")
            if len(parts) >= 2 and all(len(p) > 0 for p in parts):
                return True

        # URL pattern
        if value.startswith(("http://", "https://", "www.")):
            return True

        # Hash pattern (40 or 64 hex chars)
        if len(value) in (40, 64) and all(c in "0123456789abcdef" for c in value):
            return True

        return False

    @staticmethod
    def _is_ipv4_pattern(value: str) -> bool:
        """Quick check if value looks like IPv4."""
        parts = value.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def parse_stream(
        self,
        file_path: Path,
        skip_header: str | bool = "auto"
    ) -> Generator[list[str], None, None]:
        """
        Stream CSV file row by row (memory-efficient for large files).

        Args:
            file_path: Path to the CSV file
            skip_header: Whether to skip header row (True/False/"auto")

        Yields:
            List of values for each row

        Raises:
            FileError: If file cannot be read
            CSVError: If parsing fails
        """
        self.error_handler.validate_file(file_path)

        delimiter, encoding = self._detect_format(file_path)
        logger.info(f"Streaming with delimiter='{delimiter}', encoding={encoding}")

        first_row = True

        try:
            with open(file_path, "r", newline="", encoding=encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)

                for line_num, raw_row in enumerate(reader, start=1):
                    # Skip empty and comment lines
                    if not raw_row or all(not cell.strip() for cell in raw_row):
                        continue
                    raw_line = delimiter.join(raw_row)
                    if raw_line.strip().startswith("#"):
                        continue

                    # Handle header skipping
                    if first_row:
                        first_row = False
                        row = CSVRow(raw=raw_line, values=raw_row, line_number=line_num)
                        if self._should_skip_header(row, skip_header):
                            logger.debug(f"Line {line_num}: Skipping header in stream mode")
                            continue

                    yield raw_row

        except csv.Error as e:
            raise CSVError(f"CSV parsing error: {e}", line_number=line_num)
        except UnicodeDecodeError as e:
            raise CSVError(
                f"Encoding error: {e}. Try saving the file as UTF-8.",
                encoding=encoding
            )

    def _detect_format(self, file_path: Path) -> tuple[str, str]:
        """
        Detect CSV delimiter and encoding.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (delimiter, encoding)
        """
        # Try each encoding
        for encoding in self.encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    # Read sample for sniffer
                    sample = f.read(4096)
                    if not sample:
                        return ",", encoding  # Default for empty file

                    # Try to detect delimiter
                    try:
                        dialect = csv.Sniffer().sniff(sample, delimiters="".join(self.delimiters))
                        delimiter = dialect.delimiter
                        logger.debug(f"Sniffer detected delimiter: {repr(delimiter)}")
                        return delimiter, encoding
                    except csv.Error:
                        # Sniffer failed, try first delimiter
                        logger.debug("Sniffer failed, using first delimiter")
                        return self.delimiters[0], encoding

            except UnicodeDecodeError:
                # Try next encoding
                logger.debug(f"Encoding {encoding} failed, trying next")
                continue

        # Fallback to defaults
        logger.warning("Could not detect format, using defaults")
        return self.delimiters[0], self.encodings[0]

    def read_single_column(
        self,
        file_path: Path,
        column_index: int = 0,
        skip_header: str | bool = "auto"
    ) -> list[str]:
        """
        Read a single column from CSV file.

        Useful for files with one IoC per line.

        Args:
            file_path: Path to the CSV file
            column_index: Index of column to read (default: 0)
            skip_header: Whether to skip header row

        Returns:
            List of values from the specified column

        Raises:
            CSVError: If column index is out of range
        """
        result = self.parse(file_path, skip_header=skip_header)
        values = []

        for row in result.rows:
            if column_index < len(row.values):
                value = row.values[column_index].strip()
                if value:
                    values.append(value)
            else:
                logger.warning(f"Line {row.line_number}: Column {column_index} out of range")

        logger.info(f"Extracted {len(values)} values from column {column_index}")
        return values

    def read_all_values(
        self,
        file_path: Path,
        skip_header: str | bool = "auto"
    ) -> list[str]:
        """
        Read all values from all cells in CSV file.

        Args:
            file_path: Path to the CSV file
            skip_header: Whether to skip header row

        Returns:
            List of all non-empty values from all cells
        """
        result = self.parse(file_path, skip_header=skip_header)
        logger.info(f"Extracted {len(result.ioc_values)} total values")
        return result.ioc_values

    def validate_file(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate that a file is a valid CSV.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.parse(file_path)
            return True, None
        except FileError as e:
            return False, f"File error: {e.message}"
        except CSVError as e:
            return False, f"CSV error: {e.message}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def get_file_info(self, file_path: Path) -> dict[str, Any]:
        """
        Get detailed information about a CSV file without full parsing.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dictionary with file information
        """
        result = self.parse(file_path, skip_header="auto")

        return {
            "delimiter": result.delimiter,
            "encoding": result.encoding,
            "total_rows": result.total_rows,
            "data_rows": result.data_rows,
            "skipped_rows": result.skipped_rows,
            "header_detected": result.header_detected,
            "header_values": result.header_row.values if result.header_row else None,
            "sample_values": result.ioc_values[:5] if result.ioc_values else [],
        }

    @staticmethod
    def is_csv_file(file_path: Path) -> bool:
        """
        Quick check if file is likely a CSV based on extension.

        Args:
            file_path: Path to check

        Returns:
            True if file has CSV-like extension
        """
        csv_extensions = {".csv", ".tsv", ".txt", ".log"}
        return file_path.suffix.lower() in csv_extensions
