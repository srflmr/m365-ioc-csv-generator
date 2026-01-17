# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2025-01-18

### Added
- **Excel Multi-Sheet Support** - Full support for .xlsx/.xls files with multiple sheets
  - `excel_parser.py`: Core Excel parsing module with openpyxl
    - `ExcelSheetInfo` - Sheet metadata (name, index, row_count, estimated_ioc_count)
    - `ExcelParseResult` - Parse results with per-sheet statistics
    - `ExcelParser.get_sheets()` - Get sheet metadata without loading full data
    - `ExcelParser.parse_sheets()` - Parse specific sheets only
    - `ExcelParser.parse_all_sheets()` - Parse all sheets in workbook
    - Enhanced non-IoC filtering (comments, empty lines, N/A, NULL, single chars)
  - `sheet_selection_screen.py`: Sheet selection UI for Excel multi-sheet support
    - DataTable display with sheet metadata (name, rows, IoC count)
    - Multi-selection via checkboxes with SPACE key toggle
    - Select All / Deselect All buttons
    - Process Selected and Back buttons
    - Keyboard shortcuts: SPACE to toggle, ENTER to process, ESC to go back
    - Real-time selected count display
- **app.py**: Registered SheetSelectionScreen in SCREENS dict
- **main_screen.py**: Excel file routing to SheetSelectionScreen
  - Parses Excel file to get sheet info using ExcelParser.get_sheets()
  - Passes sheets, settings, and skip_header to SheetSelectionScreen
  - Error handling for empty workbooks
  - openpyxl availability check before processing Excel files
- **processing_screen.py**: ExcelParseResult handling in _start_processing()
  - Added excel_sheets parameter to __init__()
  - Added excel_parser instance initialization
  - Conditional CSV/Excel parsing logic
  - Combines values from multiple sheets into single list
  - Creates ParseResultCompat for unified processing workflow
- **core/__init__.py**: Added excel_parser to module exports
- **screens/__init__.py**: Updated exports to include sheet_selection_screen
- **csv_parser.py**: Enhanced non-IoC filtering to match ExcelParser
  - Added support for multiple comment markers (#, //, ;, --)
  - Added `_should_skip_value()` static method
  - Filters N/A, NULL, unknown, single characters, empty values
- **pyproject.toml**: openpyxl moved to main dependencies (auto-installed with `pip install -e .`)
- **Sample Input Files**:
  - `input/sample_mixed_data.csv` - CSV with comments and noise
  - `input/sample_network_iocs.csv` - Network IoCs with comments
  - `input/sample_ioc_collection.xlsx` - Multi-sheet Excel (4 sheets)
  - `input/sample_simple_list.xlsx` - Simple list Excel

### Changed
- Updated version from 2.7.0 to 3.0.0 (feature addition)
- ProcessingScreen now handles both CSV and Excel file types
- MainScreen routes Excel files to sheet selection instead of showing placeholder
- CSVParser comment filtering enhanced from `#` only to all patterns (#, //, ;, --)
- Both CSVParser and ExcelParser now use identical non-IoC filtering logic

### Status
- Excel multi-sheet selection fully implemented
- Users can select specific sheets or all sheets
- ProcessingScreen handles both CSV and Excel inputs seamlessly
- Sheet values are combined before IoC detection
- openpyxl is now a main dependency (auto-installed)

### Note
- Backward compatibility maintained - CSV processing path unchanged

## [2.7.0] - 2025-01-18

### Added
- **ioc_detector.py**: Comprehensive non-IoC filtering
  - Filter comments (#, //, ;, --)
  - Filter empty strings and whitespace-only values
  - Filter single-character values
  - New method `detect_batch_with_unknown()` to get both valid IoCs and unknown values
  - Better logging for unknown values with length info

### Fixed
- **ioc_detector.py**: Proper handling of URL_NO_SCHEME in detect_batch()
  - Now correctly converts URL_NO_SCHEME to URL type
  - Ensures proper export format

### Changed
- Enhanced detect_batch() to log unknown values count
- Improved debug logging for better troubleshooting

## [2.6.0] - 2025-01-18

### Fixed
- **start.bat**: Fixed apparent "stuck" issue during dependency installation
  - Root cause: pip output was redirected to log file, hiding progress from user
  - Fix: Removed output redirection to show real-time pip progress
  - Added clear message about expected wait time (1-2 minutes)
- **ioc_detector.py**: CRITICAL BUG - Fixed detect_batch() dictionary initialization
  - Root cause: Broken dict comprehension created a SET instead of DICT
  - Impact: Only 1 IoC was detected instead of all IoCs in batch
  - Fix: Initialize empty dict and build it dynamically

### Changed
- Improved user experience during dependency installation with visible progress

## [2.5.0] - 2025-01-18

### Fixed
- **start.bat**: Removed ALL PowerShell dependencies for full CMD compatibility
  - Now uses pure CMD native commands only
  - Removed timestamp comparison feature (source of parsing errors)
  - Simplified dependency check to marker file existence only
  - All paths are relative to script directory using `cd /d "%~dp0"`
  - Fully compatible with Windows CMD, no PowerShell required

### Changed
- Improved path handling in `start.bat` - always changes to script directory first
- Simplified dependency installation logic for better reliability

### Security
- N/A

## [2.4.0] - 2025-01-18

### Fixed
- Attempted to fix PowerShell parsing bug in `start.bat` timestamp comparison
- Used temporary PowerShell script file approach

### Note
- This version had parsing issues with special characters in PowerShell commands
- Superseded by v2.5.0 which removes PowerShell dependency entirely

## [2.3.0] - 2025-01-18

### Added
- `cd` to script directory at startup for consistent path handling
- Synchronized version numbers between `start.bat` and `start.sh`

### Changed
- Improved PowerShell command with explicit error handling and ExecutionPolicy
- Removed redundant SCRIPT_DIR calculation in `start.sh` (now uses pwd after cd)
- Consistent error messages and log file handling across both platforms

### Fixed
- Enhanced error handling with PowerShell ErrorActionPreference

## [2.2.0] - 2025-01-18

### Fixed
- Critical bug in `start.bat` - resolved `... was unexpected at this time` error
  - Issue: Batch file parsing error with `for` loop when comparing file timestamps
  - Fix: Use PowerShell for reliable timestamp comparison between files

## [2.1.0] - 2025-01-18

### Changed
- Improved directory creation - refactored to use loop for cleaner code
- Better error handling with consistent messaging

## [2.0.0] - 2025-01-12

### Added
- MD5 hash support (with cryptographic weakness warning)
- IoC unmasking feature (Base64, Hex, URL-encoded, Defanged, Reversed)
- Timestamped output subdirectories (e.g., `ioc_export_20250112_143022/`)
- Enhanced URL detection - added support for ftp://, ssh://, smtp://, sftp:// schemes
- Enhanced port handling - Domains/IPs with ports now properly detected as UrlNoScheme

### Changed
- **BREAKING**: URLs without scheme are now exported as-is (no auto-fix with https://)
- Updated file naming format
- Output now organized in timestamped subdirectories

### Fixed
- Reversed URL detection pattern now correctly detects reversed URLs with protocols
- Python detection in launcher scripts - improved cross-platform compatibility
  - `start.bat`: Tries multiple Python commands (python, python3, py)
  - `start.sh`: Added Windows-aware detection (python.exe, py)
  - Removed external file dependency (check_python_version.py)
  - Consolidated version validation into single step
  - Scripts use venv's Python for app launch (ensures correct environment)
  - Renamed venv directory to `.venv` (hidden by default on Unix/Linux)
  - Fixed error messages to reference `.venv` instead of `venv`

## [1.0.0] - Initial Release

### Added
- Initial release of M365 IOC CSV Generator
- Basic IoC detection (SHA256, SHA1, IPv4, Domain, URL)
- CSV parsing with smart delimiter detection
- Modern Terminal UI built with Textual framework
- File browser for interactive file selection
- Configurable output options (action, severity, expiration, RBAC groups, MITRE techniques)
- Microsoft 365 Defender compatible CSV export

---

## Version Numbering

This project uses Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## Links

- [Repository](https://github.com/srflmr/m365-ioc-csv-generator)
- [Documentation](README.md)
- [Usage Guide](USAGE.md)
