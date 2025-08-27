# Instagram Helper

Instagram Helper is a desktop tool that scrapes recent Instagram posts and saves them as searchable HTML reports.

## Features

* Scrape post content, captions, and timestamps.
* Tkinter-based interface with live progress.
* Responsive HTML reports with summaries and search.
* Supports multiple accounts in a single run.
* Works with Chrome, Brave, or Edge (via remote debugging).
* Keeps the browser session so the Instagram login remains active.
* Uses your existing browser profile with Instagram login.

## Requirements

* Python 3.12 or newer.
* Windows 10/11 (Linux/macOS supported but Windows is the focus).
* At least 4 GB RAM (8 GB recommended).
* A Chromium-based browser (Chrome, Brave, Edge).
* Playwright browser binaries (`python -m playwright install`).

## Setup

Clone the repository and create the environment:

```bash
git clone https://github.com/maximbetin/instagram-helper.git
cd instagram-helper
make setup
python -m playwright install
```

Activate the virtual environment:

```bash
. .\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate      # Linux/macOS
```

## Usage

**Important**: The app requires a browser with an active Instagram login session. Close all Chromium browsers or start one with remote debugging enabled.

### Manual browser startup (Windows PowerShell)

```powershell
& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:USERPROFILE\AppData\Local\BraveSoftware\Brave-Browser\User Data" `
  --profile-directory="Default"
```

### Run the app

```bash
instagram-helper        # console version
instagram-helper-gui    # Windows GUI, hides console window
```

Or with Makefile:

```bash
make run
```

## Development

Quality checks and tests:

```bash
make test
```

Build an executable:

```bash
make build        # or make rebuild for clean + build
```

Clean up all caches and venv:

```bash
make clean
```

## Configuration

Edit `config.py` to change defaults:

```python
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = 10
OUTPUT_DIR = Path("C:/Users/YourUsername/Desktop/ig_reports")
```

## Common Issues

| Problem              | Solution                                                  |
| -------------------- | --------------------------------------------------------- |
| Python version error | Install Python 3.12+ and check PATH                       |
| Browser not found    | Run `python -m playwright install` and update `config.py` |
| Port 9222 in use     | Close existing browser sessions or change debug port      |
| Import errors        | Activate venv and reinstall dependencies                  |

## Notes

* Developed initially on WSL2; focus is now Windows for stability.
* The tool depends on Instagram's HTML structure — breakage is possible if pages change.
* Default settings are conservative to avoid rate limits.
* Do not edit selectors in `instagram_scraper.py` unless you know what you're doing.
