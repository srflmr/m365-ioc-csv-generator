# M365 IOC CSV Generator - Complete Usage Guide

A beginner-friendly guide to using the M365 IOC CSV Generator.

---

## Table of Contents

1. [What is This Tool?](#what-is-this-tool)
2. [Installation](#installation)
3. [First Steps](#first-steps)
4. [Understanding the Interface](#understanding-the-interface)
5. [Step-by-Step Tutorial](#step-by-step-tutorial)
6. [Input File Formats](#input-file-formats)
7. [Configuration Options](#configuration-options)
8. [Output Files](#output-files)
9. [Common Use Cases](#common-use-cases)
10. [Troubleshooting](#troubleshooting)

---

## What is This Tool?

The **M365 IOC CSV Generator** is a tool that helps you create CSV files for Microsoft 365 Defender. Microsoft 365 Defender can block malicious indicators like IP addresses, domains, and URLs. This tool converts your list of bad indicators into the correct format.

### What are IoCs?

**IoC** = **Indicator of Compromise**

These are digital "fingerprints" that indicate malicious activity:
- **File Hashes** - SHA256 or SHA1 hashes of malicious files
- **IP Addresses** - IPs known to be malicious (C2 servers, botnets, etc.)
- **Domain Names** - Malicious domains (phishing, malware distribution, etc.)
- **URLs** - Full URLs to malicious content

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
- ✓ Checks Python version
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
│                  M365 IOC CSV Generator                     │
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
│  │              │  │  Output: [Separate ▼]                │ │
│  │              │  │                                       │ │
│  └──────────────┘  └─────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  📊 Summary                                              │ │
│  │  ─────────────────────────────────────────────────────  │ │
│  │  Selected File: sample_iocs.csv                         │ │
│  │  Total IoCs: 0                                          │ │
│  │  FileSha256: 0                                          │ │
│  │  IpAddress: 0                                           │ │
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
   - **Output**: `Separate` (creates one file per IoC type)

#### Step 5: Process

1. Press `Tab` to reach the **▶ Process** button
2. Press `Enter` to click it
3. Wait for processing to complete
4. View the results on the processing screen
5. Press **Back to Main** when done

#### Step 6: Find Output Files

Output files are in the `output/` folder:
```
output/
└── 20250111_143022_IpAddress_Block.csv
```

---

## Input File Formats

### Format 1: Simple List (Recommended)

Just list your indicators, one per line:

```
192.168.1.1
evil-domain.com
https://malware-site.com/download.exe
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

### Format 3: Semicolon Delimiter

```csv
indicator;value
IP;192.168.1.1
Domain;evil-domain.com
```

### Format 4: Multi-Column CSV

The tool extracts ALL values from your CSV:

```csv
timestamp,source,ip_address,domain,url,hash
2025-01-11,threat-feed,192.168.1.1,evil.com,https://malware.net,abc123...
```

All values will be extracted and categorized automatically.

### Supported IoC Types

| Type | Example | Notes |
|------|---------|-------|
| **SHA256 Hash** | `441a7bf4...c2d3` | Exactly 64 hex characters |
| **SHA1 Hash** | `da39a3ee...592fc` | Exactly 40 hex characters |
| **IPv4 Address** | `192.168.1.1` | Standard dotted decimal |
| **Domain Name** | `evil.example.com` | Any valid domain |
| **URL** | `https://evil.com/path` | With or without scheme |

### URLs Without Scheme

If you have URLs like `evil.com/path`, the tool will automatically add `https://` prefix.

---

## Configuration Options

### Action

What Microsoft 365 Defender should do with the indicator:

| Action | Description |
|--------|-------------|
| **Block** | Block the indicator (most common) |
| **Audit** | Allow but monitor for alerts |
| **Warn** | Show warning but don't block |
| **Allowed** | Explicitly allow (allowlist) |
| **BlockAndRemediate** | Block and remediate affected devices |

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

### Output Mode

How to organize output files:

| Mode | Description |
|------|-------------|
| **Separate** | One CSV file per IoC type (recommended) |
| **Combined** | All IoCs in one CSV file |
| **Both** | Create both separate and combined files |

---

## Output Files

### File Naming

Output files follow this pattern:
```
YYYYMMDD_HHMMSS_<IoCType>_<Action>.csv
```

Example: `20250111_143022_IpAddress_Block.csv`

### File Format

Each output file is a Microsoft 365 Defender compatible CSV:

```csv
IndicatorType,IndicatorValue,ExpirationTime,Action,Severity,Title,Description,...
IpAddress,192.168.1.100,,Block,High,BLOCK - IpAddress,Imported via M365 IOC Generator,...
IpAddress,10.0.0.50,,Block,High,BLOCK - IpAddress,Imported via M365 IOC Generator,...
```

### Output File Types

| File | Contents |
|------|----------|
| `FileSha256_<Action>.csv` | SHA256 hashes |
| `FileSha1_<Action>.csv` | SHA1 hashes |
| `IpAddress_<Action>.csv` | IP addresses |
| `DomainName_<Action>.csv` | Domain names |
| `Url_<Action>.csv` | URLs |
| `All_<Action>.csv` | All types combined (if Both mode) |
| `UNKNOWN.txt` | Values that couldn't be categorized |

### Maximum Rows Per File

Files are limited to **500 rows** per file (Microsoft best practice).

If you have more than 500 indicators of one type, multiple files will be created:
```
20250111_143022_IpAddress_Block_1.csv
20250111_143022_IpAddress_Block_2.csv
...
```

---

## Common Use Cases

### Use Case 1: Threat Intelligence Feed

You receive a daily threat intelligence feed with mixed IoCs.

**Input**: `daily_feed.csv` (mixed format)
```csv
timestamp,type,value
2025-01-11,ip,192.168.1.100
2025-01-11,domain,evil-c2.com
2025-01-11,hash,441a7bf47f6b5d3772b...
```

**Configuration**:
- Action: `Block`
- Severity: `High`
- Header: `Auto-detect`
- Output: `Separate`

**Result**: Separate CSV files for each type

### Use Case 2: Malware Analysis

You analyzed malware and found related IoCs.

**Input**: `malware_iocs.txt`
```
c2-server.evil.com
192.168.1.50
https://payload.evil.com/dl.exe
da39a3ee5e6b4b0d3255bfef95601890afd80709
```

**Configuration**:
- Action: `BlockAndRemediate`
- Severity: `High`
- Title: `Trojan.GenericKD.46888899`
- Description: `Trojan downloader with C2 communication`
- Output: `Separate`

**Result**: CSV files with custom title and description

### Use Case 3: Phishing Campaign

You need to block phishing domains from a campaign.

**Input**: `phishing_domains.csv`
```csv
domain
secure-login.fake-bank.com
account-verify.phishing-site.net
```

**Configuration**:
- Action: `Block`
- Severity: `High`
- Alert: `Yes`
- Output: `Separate`

**Result**: `DomainName_Block.csv` with all phishing domains

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
Title: "Threat_Feed_2025-01-11"
Title: "Phishing_Campaign_Q1"
Title: "Malware_Analysis_Case_1234"
```

### Tip 5: Check Unknown Values

Always check the `UNKNOWN.txt` file for values that couldn't be categorized.

---

## Getting Help

### Check Logs

Application logs are stored in the `logs/` folder:
```bash
logs/m365_ioc_csv.log
```

### Sample File

Use the included sample file to test:
```bash
input/sample_iocs.csv
```

### Report Issues

If you encounter bugs or have feature requests, please report them through the project's issue tracker.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE                          │
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
│    4. Find output in output/ folder                        │
│                                                             │
│  SUPPORTED IoCs:                                            │
│    • SHA256: 64 hex chars                                  │
│    • SHA1: 40 hex chars                                   │
│    • IPv4: 192.168.1.1                                    │
│    • Domain: evil.com                                     │
│    • URL: https://evil.com/path                           │
│                                                             │
│  KEYBOARD:                                                 │
│    Tab = Navigate                                          │
│    Enter = Select                                          │
│    q/Ctrl+C = Quit                                         │
│                                                             │
│  OUTPUT LOCATION:                                           │
│    output/ folder (auto-created)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**Happy IoC Hunting! 🎯**
