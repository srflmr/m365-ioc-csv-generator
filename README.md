# M365 IOC CSV Generator

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

Interactive TUI tool to generate Microsoft 365 Defender bulk import CSV files from Indicators of Compromise (IoCs).

## Features

- **Smart IoC Detection** - Automatically detects SHA256, SHA1, IPv4, Domain, and URL
- **Modern Terminal UI** - Beautiful responsive interface built with Textual
- **File Browser** - Interactive directory navigation
- **Flexible CSV Input** - Supports various delimiters and encodings
- **Configurable Output** - Custom action, severity, expiration, and more
- **Multiple Output Modes** - Separate files, combined, or both
- **Real-time Progress** - Live updates during processing

## Quick Start

### Windows
```batch
start.bat
```

### Linux / macOS
```bash
chmod +x start.sh
./start.sh
```

The launcher will automatically set up Python environment and install dependencies.

## What It Does

1. **Parse CSV** - Reads your IoC list from CSV files
2. **Detect Types** - Categorizes each indicator (hash, IP, domain, URL)
3. **Generate Output** - Creates Microsoft Defender compatible CSV files

## Basic Usage

1. Run the application
2. Browse and select a CSV file
3. Configure options (action, severity, etc.)
4. Press **▶ Process**
5. Find output files in the `output/` folder

## Input Format

Simple list (one per line):
```
192.168.1.1
evil-domain.com
https://malware-site.com
441a7bf47f6b5d3772b8d5e7b5c3f1e2a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

Or CSV with columns:
```csv
indicator,value
IP,192.168.1.1
Domain,evil-domain.com
URL,https://malware-site.com
```

## Requirements

- Python 3.10 or higher
- Windows, Linux, or macOS
- ANSI-compatible terminal

## Project Structure

```
m365-ioc-csv/
├── src/m365_ioc_csv/    # Source code
├── input/               # Sample input files
├── output/              # Generated CSV files
├── logs/               # Application logs
├── start.sh            # Linux/macOS launcher
└── start.bat           # Windows launcher
```

## Documentation

For detailed usage instructions, see [USAGE.md](USAGE.md)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Version

**Current Version:** 2.0.0
