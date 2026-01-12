# M365 IOC CSV Generator

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)]()

Interactive TUI tool to generate Microsoft 365 Defender bulk import CSV files from Indicators of Compromise (IoCs).

## Features

### Core Capabilities
- **Smart IoC Detection** - Automatically detects MD5, SHA1, SHA256, IPv4, Domain, and URL
- **IoC Unmasking** - Detects and decodes obfuscated IoCs (Base64, Hex, URL-encoded, Defanged, Reversed)
- **Modern Terminal UI** - Beautiful responsive interface built with Textual framework
- **File Browser** - Interactive directory navigation
- **Flexible CSV Input** - Supports various delimiters and encodings
- **Configurable Output** - Custom action, severity, expiration, RBAC groups, MITRE techniques
- **Timestamped Output** - Creates timestamped subdirectories for organized exports
- **Real-time Progress** - Live updates during processing

### Supported IoC Types
| Type | Format | Example |
|------|--------|---------|
| File SHA256 | 64 hex characters | `441a7bf4...` |
| File SHA1 | 40 hex characters | `441a7bf4...` |
| File MD5 | 32 hex characters | `441a7bf4...` |
| IP Address | Dotted decimal | `192.168.1.1` |
| Domain Name | FQDN | `evil.com` |
| URL | Full URL with scheme | `https://evil.com/path` |
| URL (no scheme) | With www, path, or port | `www.evil.com/path` or `evil.com:443` |

### Supported URL Schemes
- `http://` - HTTP protocol
- `https://` - HTTPS protocol
- `ftp://` - FTP protocol
- `ssh://` - SSH protocol
- `smtp://` - SMTP protocol
- `sftp://` - SFTP protocol

### IoC Unmasking Techniques
- **Base64** - `aHR0cHM6Ly9ldmlsLmNvbQ==` → `https://evil.com`
- **Hexadecimal** - `68747470733a2f2f6576696c2e636f6d` → `https://evil.com`
- **URL-encoded** - `%65%76%69%6C%2E%63%6F%6D` → `evil.com`
- **Defanged** - `hxxps://evil[.]com` → `https://evil.com`
- **Reversed** - `moc.evil//:sptth` → `https://evil.com`

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Windows, Linux, or macOS
- ANSI-compatible terminal (for TUI)

### Installation

#### Option 1: Using Launcher Scripts
**Windows:**
```batch
start.bat
```

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

#### Option 2: Manual Installation
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python -m m365_ioc_csv
```

## What It Does

1. **Parse CSV** - Reads your IoC list from CSV files with smart delimiter detection
2. **Unmask IoCs** - Detects and decodes obfuscated/masked IoC values
3. **Detect Types** - Categorizes each indicator (hash, IP, domain, URL)
4. **Generate Output** - Creates Microsoft Defender compatible CSV files in timestamped subdirectories

## Basic Usage

1. Run the application
2. Browse and select a CSV file containing IoCs
3. Configure options (action, severity, expiration, etc.)
4. Press **▶ Process**
5. Find output files in `output/ioc_export_YYYYMMDD_HHMMSS/`

## Input Format

### Simple List (one per line)
```
192.168.1.1
evil-domain.com
https://malware-site.com
www.evil.com/path
441a7bf47f6b5d3772b8d5e7b5c3f1e2a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

### CSV with Columns
```csv
indicator_type,value
domain,evil.com
url,https://malware-site.com/path
ip,192.168.1.1
file_sha256,441a7bf47f6b5d3772b8d5e7b5c3f1e2a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

### Obfuscated IoCs (Automatically Unmasked)
```csv
indicator_type,obfuscated_value
domain,aHR0cHM6Ly9ldmlsLmNvbQ==
url,hxxps://malware[.]com/path
domain,%65%76%69%6C%2E%63%6F%6D
```

## Output Structure

```
output/
└── ioc_export_20250112_143022/
    ├── M365_IOC_FileSha256_Block_20250112_143022.csv
    ├── M365_IOC_FileSha1_Block_20250112_143022.csv
    ├── M365_IOC_FileMd5_Block_20250112_143022.csv
    ├── M365_IOC_IpAddress_Block_20250112_143022.csv
    ├── M365_IOC_DomainName_Block_20250112_143022.csv
    ├── M365_IOC_Url_Block_20250112_143022.csv
    └── M365_IOC_UNKNOWN_20250112_143022.txt
```

## URL Handling

### URL Detection Rules
- URLs **with** scheme (`http://`, `https://`, `ftp://`, etc.) → Exported as `Url`
- URLs **without** scheme but with path, `www.` prefix, or port → Exported as `Url` (URL_NO_SCHEME)
- Domain-only values (no path, no `www.`, no port) → Exported as `DomainName`

### Port Handling
Domains and IPs with ports are now properly detected:
- `evil.com:443` → UrlNoScheme → Url CSV
- `example.com:8080/path` → UrlNoScheme → Url CSV
- `192.168.1.1:8080` → UrlNoScheme → Url CSV
- `ftp://files.com:21` → Url → Url CSV

### Examples
| Input | Detected As | Exported As |
|-------|-------------|-------------|
| `https://evil.com/path` | Url | `https://evil.com/path` |
| `http://example.com` | Url | `http://example.com` |
| `ftp://files.com:21` | Url | `ftp://files.com:21` |
| `www.evil.com/path` | Url (no scheme) | `www.evil.com/path` |
| `evil.com/path` | Url (no scheme) | `evil.com/path` |
| `www.evil.com` | Url (no scheme) | `www.evil.com` |
| `evil.com:443` | Url (no scheme) | `evil.com:443` |
| `192.168.1.1:8080` | Url (no scheme) | `192.168.1.1:8080` |
| `evil.com` | DomainName | `evil.com` |

> **Note:** URLs without scheme are exported as-is. Microsoft Defender handles URL normalization internally based on threat intelligence.

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| Action | Action to take | Block |
| Severity | Severity level | High |
| Expiration | When indicator expires | Never |
| Generate Alert | Create alert on match | Yes |
| RBAC Groups | Device group targeting | All devices |
| MITRE Techniques | MITRE ATT&CK tags | None |
| Custom Title | Custom indicator title | Auto-generated |
| Custom Description | Custom description | Auto-generated |
| Max Rows Per File | Split large exports | 500 |

## Project Structure

```
m365-ioc-csv/
├── src/m365_ioc_csv/
│   ├── core/              # Core logic modules
│   │   ├── ioc_detector.py      # IoC type detection
│   │   ├── ioc_unmasker.py      # Obfuscation unmasking
│   │   ├── csv_parser.py        # CSV parsing
│   │   ├── csv_writer.py        # CSV generation
│   │   └── config.py            # Configuration
│   ├── tui/               # Terminal UI
│   │   ├── screens/             # UI screens
│   │   ├── widgets/             # Custom widgets
│   │   └── styles/              # UI styling
│   ├── utils/             # Utilities
│   └── app.py             # Main application
├── input/                # Sample input files
├── output/               # Generated CSV files
├── logs/                # Application logs
├── tests/               # Unit tests
├── start.sh             # Linux/macOS launcher
├── start.bat            # Windows launcher
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Documentation

For detailed usage instructions, see [USAGE.md](USAGE.md)

## Platform Support

- **Windows** 10/11 with WSL or native Python
- **Linux** (Ubuntu, Debian, RHEL, etc.)
- **macOS** 10.15+

## License

MIT License - see [LICENSE](LICENSE) file for details

## Version

**Current Version:** 2.0.0

### Changelog

#### v2.0.0 (Current)
- Added MD5 hash support
- Added IoC unmasking (Base64, Hex, URL-encoded, Defanged, Reversed)
- Changed output to timestamped subdirectories
- Removed auto-fix for URLs without scheme (export as-is)
- Updated file naming format
- **Enhanced URL detection** - Added support for ftp://, ssh://, smtp://, sftp:// schemes
- **Enhanced port handling** - Domains/IPs with ports now properly detected as UrlNoScheme
- **Fixed reversed URL detection** - Pattern now correctly detects reversed URLs with protocols

#### v1.0.0
- Initial release
