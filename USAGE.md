# M365 IOC CSV Generator - Complete Usage Guide

A comprehensive guide to using the M365 IOC CSV Generator v2.0.

---

## Table of Contents

1. [What is This Tool?](#what-is-this-tool)
2. [Installation](#installation)
3. [First Steps](#first-steps)
4. [Understanding the Interface](#understanding-the-interface)
5. [Step-by-Step Tutorial](#step-by-step-tutorial)
6. [Input File Formats](#input-file-formats)
7. [IoC Detection & Classification](#ioc-detection--classification)
8. [IoC Unmasking](#ioc-unmasking)
9. [Configuration Options](#configuration-options)
10. [Output Files](#output-files)
11. [Common Use Cases](#common-use-cases)
12. [Troubleshooting](#troubleshooting)

---

## What is This Tool?

The **M365 IOC CSV Generator** is a tool that helps you create CSV files for Microsoft 365 Defender. Microsoft 365 Defender can block malicious indicators like IP addresses, domains, and URLs. This tool converts your list of bad indicators into the correct format.

### What are IoCs?

**IoC** = **Indicator of Compromise**

These are digital "fingerprints" that indicate malicious activity:
- **File Hashes** - MD5, SHA1, or SHA256 hashes of malicious files
- **IP Addresses** - IPs known to be malicious (C2 servers, botnets, etc.)
- **Domain Names** - Malicious domains (phishing, malware distribution, etc.)
- **URLs** - Full URLs to malicious content

### New in v2.0

- **MD5 Hash Support** - Detect MD5 hashes (with warning about cryptographic weakness)
- **IoC Unmasking** - Automatically detects and decodes obfuscated IoCs
- **Timestamped Output** - Creates timestamped subdirectories for organized exports
- **No URL Auto-Fix** - URLs without scheme are exported as-is (Microsoft handles normalization)

---

## Installation

### Method 1: Auto-Setup (Recommended - Easiest)

#### Windows
1. Download the project
2. Double-click `start.bat`
3. Wait for automatic setup
4. Application opens automatically

#### Linux / macOS
```bash
# Navigate to project folder
cd m365-ioc-csv

# Make launcher executable (first time only)
chmod +x start.sh

# Run the application
./start.sh
```

The launcher handles everything:
- ✓ Checks Python version (requires 3.10+)
- ✓ Creates virtual environment
- ✓ Installs dependencies
- ✓ Launches the application

### Method 2: Manual Installation

If auto-setup doesn't work:

#### Step 1: Install Python
- **Windows**: Download from [python.org](https://www.python.org/downloads/) - Check "Add Python to PATH"
- **Ubuntu/Debian**: `sudo apt install python3 python3-venv`
- **Fedora**: `sudo dnf install python3 python3-venv`
- **macOS**: `brew install python3`

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```

#### Step 3: Activate Virtual Environment
```bash
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
pip install textual rich
```

#### Step 5: Run Application
```bash
python -m m365_ioc_csv
```

---

## First Steps

### 1. Prepare Your Input File

Create a CSV file with your indicators. See [Input File Formats](#input-file-formats) for examples.

### 2. Launch the Application

Run `start.bat` (Windows) or `./start.sh` (Linux/macOS)

### 3. Navigate the Interface

Use arrow keys to navigate. Press `Tab` to move between panels. Press `Enter` or `Space` to select.

### 4. Exit the Application

Press `q` or `Ctrl+C` at any time, or click the **⏻ Exit** button.

---

## Understanding the Interface

```
┌─────────────────────────────────────────────────────────────┐
│                  M365 IOC CSV Generator v2.0                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌─────────────────────────────────────┐ │
│  │              │  │  📄 File Information                 │ │
│  │   📁 Files   │  │  ───────────────────────────────────  │ │
│  │              │  │  File: sample_iocs.csv               │ │
│  │   /home/...  │  │  Delimiter: ','                      │ │
│  │              │  │  Total Rows: 15                      │ │
│  │   input/     │  │  Header: YES (auto-detected)         │ │
│  │   output/    │  │                                       │ │
│  │              │  │  ⚙️ Configuration                     │ │
│  │              │  │  ───────────────────────────────────  │ │
│  │   ▶ sample_  │  │  Action: [Block ▼]                   │ │
│  │   test.csv   │  │  Severity: [High ▼]                  │ │
│  │   data.csv   │  │  Header: [Auto-detect ▼]              │ │
│  │              │  │  Title: [Your custom title...]       │ │
│  │              │  │  Description: [Add description...]    │ │
│  │              │  │  Expiration: [Never ▼]               │ │
│  │              │  │  Alert: [Yes ▼]                      │ │
│  └──────────────┘  └─────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  📊 Summary                                              │ │
│  │  ─────────────────────────────────────────────────────  │ │
│  │  Selected File: sample_iocs.csv                         │ │
│  │  Total IoCs: 0                                          │ │
│  │  FileSha256: 0  FileSha1: 0  FileMd5: 0                 │ │
│  │  IpAddress: 0                                           │ │
│  │  DomainName: 0  Url: 0                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  [▶ Process] [✕ Clear] [↻ Refresh] [⏻ Exit]           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Panels Explained

| Panel | Purpose |
|-------|---------|
| **📁 Files** | Browse directories and select CSV files |
| **📄 File Information** | Shows details about selected file |
| **⚙️ Configuration** | Set output options |
| **📊 Summary** | Shows detected IoC counts after processing |

### Buttons Explained

| Button | Function |
|--------|----------|
| **▶ Process** | Start processing the selected file |
| **✕ Clear** | Clear selection and reset all fields |
| **↻ Refresh** | Refresh the file browser (shows new files) |
| **⏻ Exit** | Exit the application |

---

## Step-by-Step Tutorial

### Scenario: Blocking Malicious IPs

You have a list of malicious IP addresses and want to block them in Microsoft 365 Defender.

#### Step 1: Create Input File

Create a file called `malicious_ips.csv`:
```csv
192.168.1.100
10.0.0.50
172.16.0.1
203.0.113.5
```

#### Step 2: Launch Application

Run `start.bat` or `./start.sh`

#### Step 3: Select Your File

1. Use arrow keys to navigate the **📁 Files** panel
2. Press `Enter` to open directories
3. Navigate to where you saved `malicious_ips.csv`
4. Press `Enter` on the file to select it

#### Step 4: Configure Options

1. Press `Tab` to move to the **⚙️ Configuration** panel
2. Set your preferences:
   - **Action**: `Block` (already selected)
   - **Severity**: `High` (already selected)
   - **Header**: `Auto-detect` (recommended)
   - **Title**: Leave empty for auto-generated title
   - **Description**: Leave empty for default description
   - **Expiration**: `Never` (or choose duration)
   - **Alert**: `Yes` (recommended)

#### Step 5: Process

1. Press `Tab` to reach the **▶ Process** button
2. Press `Enter` to click it
3. Wait for processing to complete
4. View the results on the processing screen
5. Press **Back to Main** when done

#### Step 6: Find Output Files

Output files are in the `output/` folder in a timestamped subdirectory:
```
output/
└── ioc_export_20250112_143022/
    └── M365_IOC_IpAddress_Block_20250112_143022.csv
```

---

## Input File Formats

### Format 1: Simple List (Recommended)

Just list your indicators, one per line:

```
192.168.1.1
evil-domain.com
https://malware-site.com/download.exe
www.evil.com/path
441a7bf47f6b5d3772b8d5e7b5c3f1e2a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

### Format 2: CSV with Headers

```csv
indicator,value
IP,192.168.1.1
Domain,evil-domain.com
URL,https://malware-site.com
FileSha256,441a7bf47f6b5d3772b8d5e7b5c3f1e2a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

### Format 3: Obfuscated IoCs (Automatically Unmasked)

```csv
indicator_type,obfuscated_value
domain,aHR0cHM6Ly9ldmlsLmNvbQ==
url,hxxps://malware[.]com/path
domain,%65%76%69%6C%2E%63%6F%6D
hash,68747470733a2f2f6576696c2e636f6d
```

### Format 4: Semicolon Delimiter

```csv
indicator;value
IP;192.168.1.1
Domain;evil-domain.com
```

### Format 5: Multi-Column CSV

The tool extracts ALL values from your CSV:

```csv
timestamp,source,ip_address,domain,url,hash
2025-01-11,threat-feed,192.168.1.1,evil.com,https://malware.net,abc123...
```

All values will be extracted, unmasked (if obfuscated), and categorized automatically.

---

## IoC Detection & Classification

### Supported IoC Types

| Type | Format | Example | Notes |
|------|--------|---------|-------|
| **File SHA256** | 64 hex characters | `441a7bf4...c2d3` | Most secure hash |
| **File SHA1** | 40 hex characters | `da39a3ee...592fc` | Secure hash |
| **File MD5** | 32 hex characters | `d41d8cd98f00b204...` | ⚠️ Weak, deprecated |
| **IPv4 Address** | Dotted decimal | `192.168.1.1` | Standard format |
| **Domain Name** | FQDN | `evil.example.com` | Without path |
| **URL** | With or without scheme | `https://evil.com/path` or `www.evil.com/path` | As-is export |

### Detection Priority

The tool detects IoCs in this order:
1. **URL with scheme** - `http://` or `https://`
2. **SHA256 Hash** - 64 hex characters
3. **SHA1 Hash** - 40 hex characters
4. **MD5 Hash** - 32 hex characters (logged with warning)
5. **IPv4 Address** - Dotted decimal format
6. **URL without scheme** - `www.xxx` or contains `/`
7. **Domain Name** - Domain only (no path, no `www.`)

### URL Handling Rules

| Input | Detected As | Exported As | Notes |
|-------|-------------|-------------|-------|
| `https://evil.com/path` | Url | `https://evil.com/path` | As-is |
| `http://example.com` | Url | `http://example.com` | As-is |
| `www.evil.com/path` | Url (no scheme) | `www.evil.com/path` | **As-is** (no auto-fix) |
| `evil.com/path` | Url (no scheme) | `evil.com/path` | **As-is** (no auto-fix) |
| `www.evil.com` | Url (no scheme) | `www.evil.com` | **As-is** (no auto-fix) |
| `evil.com` | DomainName | `evil.com` | As-is |

> **Important Change in v2.0**: URLs without scheme are **NOT** auto-fixed with `https://`. They are exported as-is. Microsoft Defender handles URL normalization internally based on threat intelligence.

---

## IoC Unmasking

### What is IoC Unmasking?

Threat intelligence reports often contain obfuscated (masked) IoCs to prevent accidental clicks. This tool automatically detects and decodes these obfuscations.

### Supported Unmasking Techniques

| Technique | Example Input | Unmasked Output | Confidence |
|-----------|---------------|-----------------|------------|
| **Base64** | `aHR0cHM6Ly9ldmlsLmNvbQ==` | `https://evil.com` | High (0.8) |
| **Hexadecimal** | `68747470733a2f2f6576696c2e636f6d` | `https://evil.com` | Medium (0.7) |
| **URL-encoded** | `%65%76%69%6C%2E%63%6F%6D` | `evil.com` | High (0.95) |
| **Defanged** | `hxxps://evil[.]com` | `https://evil.com` | Very High (1.0) |
| **Reversed** | `moc.evil//:sptth` | `https://evil.com` | Low (0.42) |

### Defanged URL Patterns

| Pattern | Description | Fixed To |
|---------|-------------|----------|
| `hxxp://` | Protocol obfuscation | `http://` |
| `hxxps://` | Protocol obfuscation | `https://` |
| `[.]` | Bracketed dot | `.` |
| `[/]` | Context-dependent | `.` in domain, `/` in path |
| `(dot)` | Parenthesized dot | `.` |
| `(.)` | Parenthesized bracketed dot | `.` |

### Example: Obfuscated Input Processing

**Input CSV:**
```csv
indicator_type,obfuscated_value
domain,aHR0cHM6Ly9ldmlsLmNvbQ==
url,hxxps://malware[.]com/path
domain,%65%76%69%6C%2E%63%6F%6D
```

**Processing Flow:**
```
1. Parse CSV → Extract values
2. Detect obfuscation → is_masked() check
3. Unmask each value:
   - aHR0cHM6Ly9ldmlsLmNvbQ== → https://evil.com (Base64)
   - hxxps://malware[.]com/path → https://malware.com/path (Defanged)
   - %65%76%69%6C%2E%63%6F%6D → evil.com (URL-encoded)
4. Detect IoC types → Classification
5. Generate CSV files
```

---

## Configuration Options

### Action

What Microsoft 365 Defender should do with the indicator:

| Action | Description | Use Case |
|--------|-------------|----------|
| **Block** | Block the indicator | Most common |
| **Audit** | Allow but monitor | Testing/monitoring |
| **Warn** | Show warning but don't block | User awareness |
| **Allowed** | Explicitly allow | Allowlist |
| **BlockAndRemediate** | Block and remediate | Active threat |

### Severity

Threat level for the indicator:

| Severity | Description | Use Case |
|----------|-------------|----------|
| **High** | Severe threat | Known malware, C2 servers |
| **Medium** | Moderate threat | Suspicious domains |
| **Low** | Low threat | Potentially malicious |
| **Informational** | Info only | Research purposes |

### Header Handling

How to treat the first row of your CSV:

| Option | Description |
|--------|-------------|
| **Auto-detect** | Automatically detect if first row is a header |
| **Always skip** | Always skip first row |
| **Never skip** | Include first row as data |

### Custom Title & Description

Add custom information to your indicators:
- **Title**: Custom name for this indicator set
- **Description**: Additional context about the threat

Leave empty for auto-generated values.

### Expiration

When indicators should expire:

| Option | Description |
|--------|-------------|
| **Never** | Indicators never expire |
| **30 days** | Expire after 30 days |
| **90 days** | Expire after 90 days |
| **180 days** | Expire after 180 days |
| **365 days** | Expire after 1 year |

### Generate Alert

Create Microsoft 365 Defender alerts when indicators are triggered:
- **Yes**: Create alerts (recommended)
- **No**: Don't create alerts

### Advanced Options

| Setting | Description | Default |
|----------|-------------|---------|
| **RBAC Groups** | Target specific device groups | All devices |
| **MITRE Techniques** | Add MITRE ATT&CK tags | None |
| **Max Rows Per File** | Split large exports | 500 |

---

## Output Files

### Output Structure

```
output/
└── ioc_export_YYYYMMDD_HHMMSS/
    ├── M365_IOC_FileSha256_Block_YYYYMMDD_HHMMSS.csv
    ├── M365_IOC_FileSha1_Block_YYYYMMDD_HHMMSS.csv
    ├── M365_IOC_FileMd5_Block_YYYYMMDD_HHMMSS.csv
    ├── M365_IOC_IpAddress_Block_YYYYMMDD_HHMMSS.csv
    ├── M365_IOC_DomainName_Block_YYYYMMDD_HHMMSS.csv
    ├── M365_IOC_Url_Block_YYYYMMDD_HHMMSS.csv
    └── M365_IOC_UNKNOWN_YYYYMMDD_HHMMSS.txt
```

### File Naming Convention

```
M365_IOC_<IoCType>_<Action>_<Timestamp>.csv
```

Example: `M365_IOC_IpAddress_Block_20250112_143022.csv`

### File Format

Each output file is a Microsoft 365 Defender compatible CSV:

```csv
IndicatorType,IndicatorValue,Action,Severity,Title,Description,ExpirationTime,GenerateAlert,...
IpAddress,192.168.1.100,Block,High,BLOCK - IpAddress,Imported via M365 IOC Generator,,True,...
IpAddress,10.0.0.50,Block,High,BLOCK - IpAddress,Imported via M365 IOC Generator,,True,...
```

### Maximum Rows Per File

Files are limited to **500 rows** per file (Microsoft best practice).

If you have more than 500 indicators of one type, multiple files will be created:
```
M365_IOC_IpAddress_Block_20250112_143022_000.csv
M365_IOC_IpAddress_Block_20250112_143022_001.csv
...
```

### Output File Types

| File | Contents | Description |
|------|----------|-------------|
| `M365_IOC_FileSha256_*.csv` | SHA256 hashes | File indicators |
| `M365_IOC_FileSha1_*.csv` | SHA1 hashes | File indicators |
| `M365_IOC_FileMd5_*.csv` | MD5 hashes | File indicators (weak) |
| `M365_IOC_IpAddress_*.csv` | IP addresses | Network indicators |
| `M365_IOC_DomainName_*.csv` | Domain names | Domain indicators |
| `M365_IOC_Url_*.csv` | URLs | URL indicators |
| `M365_IOC_UNKNOWN_*.txt` | Uncategorized values | Review needed |

---

## Common Use Cases

### Use Case 1: Threat Intelligence Feed with Obfuscated IoCs

You receive a daily threat intelligence feed with mixed, obfuscated IoCs.

**Input**: `daily_feed.csv`
```csv
timestamp,type,obfuscated_value
2025-01-12,ip,aHR0cHM6Ly9ldmlsLmNvbQ==
2025-01-12,domain,hxxps://malware[.]com
2025-01-12,hash,%65%76%69%6C%2E%63%6F%6D
```

**Configuration**:
- Action: `Block`
- Severity: `High`
- Header: `Auto-detect`

**Result**: Separate CSV files with unmasked IoCs

### Use Case 2: Malware Analysis

You analyzed malware and found related IoCs.

**Input**: `malware_iocs.txt`
```
c2-server.evil.com
192.168.1.50
www.payload.evil.com/dl.exe
d41d8cd98f00b204e9800998ecf8427e
```

**Configuration**:
- Action: `BlockAndRemediate`
- Severity: `High`
- Title: `Trojan.GenericKD.46888899`
- Description: `Trojan downloader with C2 communication`

**Result**: CSV files with custom title and description

### Use Case 3: Phishing Campaign

You need to block phishing domains from a campaign.

**Input**: `phishing_domains.csv`
```csv
domain
secure-login.fake-bank.com
account-verify.phishing-site.net
www.bank-login-scam.com
```

**Configuration**:
- Action: `Block`
- Severity: `High`
- Alert: `Yes`

**Result**: `M365_IOC_DomainName_Block_*.csv` with all phishing domains

### Use Case 4: Mixed IoCs from Threat Report

You have a threat report with various obfuscated IoCs.

**Input**: `threat_report.csv`
```csv
indicator_type,value
domain,aHR0cHM6Ly9ldmlsLmNvbQ==
url,hxxp://phishing[.]site[.]com/login
ip,%31%39%32%2E%31%36%38%2E%31%2E%31
hash,68747470733a2f2f6576696c2e636f6d
```

**Processing**:
1. Base64 decoded → `https://evil.com` (DomainName or Url depending on value)
2. Defanged → `http://phishing.site.com/login` (Url)
3. URL-encoded → `192.168.1.1` (IpAddress)
4. Hex decoded → `https://evil.com` (Url)

---

## Troubleshooting

### "Python not found"

**Problem**: System can't find Python

**Solution**:
- **Windows**: Install from [python.org](https://www.python.org/downloads/) - Check "Add Python to PATH"
- **Linux**: `sudo apt install python3`
- **macOS**: `brew install python3`

### "No file selected"

**Problem**: Process button does nothing

**Solution**:
1. Browse the file panel
2. Select a CSV file by pressing `Enter`
3. Look at "File Information" panel to confirm selection
4. Then press Process button

### "Permission denied"

**Problem**: Can't write to output directory

**Solution**:
- Ensure you have write permissions
- On Linux/macOS: `chmod +w output/`
- On Windows: Run as Administrator if needed

### "CSV parsing failed"

**Problem**: File can't be parsed

**Solution**:
1. Check file encoding (should be UTF-8)
2. Ensure delimiter is consistent
3. Verify quoted values are properly closed
4. Try opening in a text editor to check format

### Terminal display issues

**Problem**: UI looks broken or garbled

**Solution**:
- Increase terminal size (minimum 80x25, recommended 120x40)
- Use a modern terminal (Windows Terminal, iTerm2, etc.)
- Ensure terminal supports ANSI colors

### No IoCs detected

**Problem**: Processing completes but 0 IoCs found

**Solution**:
1. Check your input file format
2. Verify values match IoC patterns
3. Check "File Information" panel for row count
4. Try with sample file from `input/` folder

### IoCs detected as UNKNOWN

**Problem**: Values end up in UNKNOWN.txt

**Solution**:
1. Check if values match supported IoC patterns
2. Verify hashes are correct length (32/40/64 hex chars)
3. Ensure domains have valid TLD (2+ chars)
4. Check if URLs are properly formatted

### URLs not exported correctly

**Problem**: URLs without scheme don't have `https://` prefix

**Solution**:
This is **intentional behavior in v2.0**. URLs without scheme are exported as-is. Microsoft Defender handles URL normalization. If you need a specific scheme, include it in your input file.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Move between panels/widgets |
| `Arrow Keys` | Navigate within widget |
| `Enter` | Select item / Click button |
| `Space` | Toggle checkbox / Select button |
| `Escape` | Go back / Close modal |
| `q` | Quit application |
| `Ctrl+C` | Force quit |

---

## Tips & Tricks

### Tip 1: Refresh File Browser

Added a new file while app is running? Press **↻ Refresh** to see it.

### Tip 2: Quick Testing

Use the sample file in `input/sample_iocs.csv` to test the application.

### Tip 3: Bulk Processing

Process multiple files by:
1. Process first file
2. Press "Back to Main"
3. Select next file
4. Repeat

### Tip 4: Custom Titles for Tracking

Use custom titles to track indicator sources:
```
Title: "Threat_Feed_2025-01-12"
Title: "Phishing_Campaign_Q1"
Title: "Malware_Analysis_Case_1234"
```

### Tip 5: Check Unknown Values

Always check the `M365_IOC_UNKNOWN_*.txt` file for values that couldn't be categorized.

### Tip 6: Handle Obfuscated IoCs

The tool automatically unmaskes common obfuscations. No manual preprocessing needed!

### Tip 7: MD5 Hash Warning

When MD5 hashes are detected, a warning is logged. MD5 is cryptographically broken. Prefer SHA256 or SHA1 when possible.

---

## Getting Help

### Check Logs

Application logs are stored in the `logs/` folder:
```bash
logs/M365_IOC_CSV_YYYYMMDD.log
```

### Sample Files

Use the included sample files to test:
```bash
input/sample_iocs.csv        # Basic IoC types
input/test_masked_iocs.csv   # Obfuscated IoCs
input/test_md5_iocs.csv      # MD5 hashes
```

### Report Issues

If you encounter bugs or have feature requests, please report them through the project's issue tracker.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE (v2.0)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INSTALL:                                                   │
│    Windows: Double-click start.bat                        │
│    Linux/mac: ./start.sh                                   │
│                                                             │
│  BASIC WORKFLOW:                                            │
│    1. Select CSV file from file browser                    │
│    2. Configure options (or use defaults)                   │
│    3. Press ▶ Process                                      │
│    4. Find output in output/ioc_export_YYYYMMDD_HHMMSS/    │
│                                                             │
│  SUPPORTED IoCs:                                            │
│    • SHA256: 64 hex chars                                  │
│    • SHA1: 40 hex chars                                   │
│    • MD5: 32 hex chars (⚠ weak)                          │
│    • IPv4: 192.168.1.1                                    │
│    • Domain: evil.com                                     │
│    • URL: https://evil.com/path or www.evil.com/path      │
│                                                             │
│  UNMASKING SUPPORTS:                                        │
│    • Base64: aHR0cHM6Ly9...                               │
│    • Hex: 68747470...                                     │
│    • URL-encoded: %65%76...                                │
│    • Defanged: hxxp://evil[.]com                           │
│    • Reversed: moc.evil//:sptth                            │
│                                                             │
│  KEYBOARD:                                                 │
│    Tab = Navigate                                          │
│    Enter = Select                                          │
│    q/Ctrl+C = Quit                                         │
│                                                             │
│  OUTPUT:                                                   │
│    output/ioc_export_YYYYMMDD_HHMMSS/                     │
│    M365_IOC_<Type>_<Action>_<Timestamp>.csv                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**Happy IoC Hunting! 🎯**
