# Instagram Helper

[![Build Executable](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/maximbetin/instagram-helper/actions/workflows/ci.yml)

A tool that automatically fetches recent posts from specified Instagram accounts and generates a
stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified Instagram accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Global date sorting**: All posts are sorted by date across all accounts (newest first)
- **Interactive report**: HTML report includes copy-to-clipboard functionality for post links and
  captions
- **Progress tracking**: Real-time console output showing processing progress
- **CLI interface**: Command-line options for flexible usage
- **Environment configuration**: Support for environment variables

## Installation

### Quick Setup (Recommended)

For development and testing:

```bash
# Clone the repository
git clone <your-repo-url>
cd instagram-helper

# Run the automated setup script (WSL2 optimized)
./scripts/setup_dev.sh

# Or use the Makefile
make dev-setup
```

### Manual Setup

#### Step 1: Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Install the package with development dependencies

```bash
pip install -e ".[dev]"
```

#### Step 3: Install Playwright browsers

```bash
playwright install
```

#### Runtime Dependencies Only

For production use:

```bash
pip install -e .
playwright install
```

**Note:** The tool is configured to use Brave browser by default. If you don't have Brave installed,
you can change the browser path in `config.py` or set the `BROWSER_PATH` environment variable.

## Usage

### Basic Usage

#### Step 1: Run the script with default settings

```bash
python cli.py
```

#### Step 2: Or use the CLI interface for more options

```bash
python cli.py --help
```

#### Step 3: Or install the package and use the command-line tool

```bash
pip install -e .
instagram-helper
```

**Default Behavior**:

- Fetches posts from the last 3 days
- Processes all configured Instagram accounts
- Saves HTML reports and logs to `Desktop/IG Helper/`
- Automatically opens the generated report

### CLI Options

```bash
python cli.py [OPTIONS]

Options:
  --days, -d INT          Number of days back to fetch posts from (default: 3)
  --accounts, -a TEXT...  Specific Instagram accounts to fetch from
  --output, -o PATH       Output directory for reports (default: Desktop/IG Helper)
  --log-dir PATH          Directory for log files (default: Desktop/IG Helper)
  --no-open               Do not automatically open the generated report
  --verbose, -v           Enable verbose logging
  --help                  Show this message and exit
```

### Examples

```bash
# Use default settings (saves to Desktop/IG Helper folder)
python cli.py

# Fetch posts from last 3 days
python cli.py --days 3

# Only fetch from specific accounts
python cli.py --accounts gijon biodevas

# Save reports to custom directory
python cli.py --output ./reports

# Don't automatically open the report
python cli.py --no-open

# Enable verbose logging
python cli.py --verbose
```

### WSL2 → Windows Brave (reuse Windows session)

When running from WSL2, you can attach to an already-running Brave on Windows to reuse your
logged-in session and cookies.

#### Expose DevTools from Windows Brave

There are two reliable options:

1. Bind DevTools to all interfaces (simplest)

   ```powershell
   Stop-Process -Name brave -Force -ErrorAction SilentlyContinue
   & "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" \
     --remote-debugging-port=9222 \
     --remote-debugging-address=0.0.0.0
   ```

   Verify:

   ```powershell
   netstat -ano | findstr :9222
   ```

1. Keep loopback-only and add a Windows portproxy (safer)

   - Start Brave on loopback:

     ```powershell
     Stop-Process -Name brave -Force -ErrorAction SilentlyContinue
      & "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" \
        --remote-debugging-port=9222
     ```

   - Add a portproxy on the Windows vEthernet (WSL) IP (get it via `ipconfig`, usually 172.x.x.x):

     ```powershell
     netsh interface portproxy reset
      netsh interface portproxy add v4tov4 ^
        listenaddress=0.0.0.0 listenport=9222 ^
        connectaddress=127.0.0.1 connectport=9222
     netsh interface portproxy show all
     ```

   - Allow firewall (optional but recommended):

     ```powershell
      netsh advfirewall firewall add rule ^
        name="Allow Brave DevTools 9222" dir=in action=allow ^
        protocol=TCP localport=9222
     ```

#### Connect from WSL2 (recommended defaults)

1. Start Brave on Windows with DevTools port open (can be started from WSL2 too):

```powershell
& "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" `
  --remote-debugging-port=9222 `
  --remote-debugging-address=0.0.0.0
```

2. Then in WSL2, run the tool normally. It will connect over CDP to the Windows Brave:

```bash
export BROWSER_REMOTE_HOST=172.19.192.1
python -u cli.py --days 3 -v
```

#### Get the Windows host IP inside WSL2 and export environment variables for this project

```bash
# Optional: The app auto-detects WSL and enables attach-only by default.
# You can still set the host explicitly if needed:
export WSL_HOST_IP=$(awk '/nameserver/ {print $2; exit}' /etc/resolv.conf)
export BROWSER_REMOTE_HOST="$WSL_HOST_IP"  # optional override
```

1. Run the tool normally. It will connect over CDP to the Windows Brave:

```bash
python cli.py
```

Notes:

- If you prefer to lock down the DevTools port, restrict it in Windows Firewall to your WSL IP only.
- When running inside WSL, the app defaults to attach-only mode to reuse your Windows browser
  session. Leave `BROWSER_PATH` unset in this mode; the app will not spawn a local browser.
- If `BROWSER_REMOTE_HOST` is not set and `BROWSER_ATTACH_ONLY=true`, the app will attempt to
  auto-detect the Windows host IP from `/etc/resolv.conf`.

#### Troubleshooting WSL2 attach

1. Confirm Windows is listening:

   ```powershell
   netstat -ano | findstr :9222
   ```

1. From WSL2, probe the endpoint:

   ```bash
   curl "http://$(awk '/nameserver/ {print $2; exit}' /etc/resolv.conf):9222/json/version"
   # or, if using portproxy on the vEthernet IP from Windows ipconfig (e.g., 172.19.192.1):
   curl "http://172.19.192.1:9222/json/version"
   ```

1. If curl fails, check Windows Firewall and the portproxy configuration:

   ```powershell
   netsh interface portproxy show all
   netsh advfirewall firewall show rule name="Allow Brave DevTools 9222"
   ```

## Configuration

### Environment Variables

You can configure the tool using environment variables:

```bash
# Browser settings
export BROWSER_DEBUG_PORT=9222
export BROWSER_LOAD_DELAY=5000     # milliseconds
export BROWSER_LOAD_TIMEOUT=15000  # milliseconds
export BROWSER_PATH="/usr/bin/brave-browser"  # Or any Chromium-based browser
export BROWSER_ATTACH_ONLY=true    # Attach to an existing browser (skip launching locally)
export BROWSER_REMOTE_HOST="172.19.192.1"  # Windows vEthernet (WSL) IP or nameserver IP
export BROWSER_CONNECT_SCHEME="http"       # http or ws (http is typical for Chromium-based)

# Instagram settings
export INSTAGRAM_POST_LOAD_DELAY=3000         # milliseconds
export INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3
export INSTAGRAM_POST_LOAD_TIMEOUT=20000      # milliseconds
export INSTAGRAM_ACCOUNT_LOAD_DELAY=3000      # milliseconds
export INSTAGRAM_RETRY_DELAY=2000             # milliseconds
export INSTAGRAM_URL="https://www.instagram.com/"

# Output settings
export OUTPUT_DIR="/path/to/output"
export LOG_DIR="/path/to/logs"
export TIMEZONE_OFFSET=2
```

### Configuration File

Edit `config.py` to modify:

- **Post Fetching Settings**: Days back to fetch (default: 3), max posts per account (default: 3),
  load delays
- **Instagram Accounts**: List of usernames to fetch posts from (currently configured for Asturias
  cultural accounts)
- **Browser Settings**: Browser path (default: Brave), debug port, timeouts
- **Output Settings**: Output and log directories (default: Desktop/IG Helper)

## Output

The tool generates an interactive HTML report and detailed logs:

**HTML Report**:

- Summary statistics (total accounts checked, total posts found, date range)
- All posts sorted by date (newest first) with captions, dates, and account information
- Direct links to original Instagram posts
- Copy-to-clipboard buttons for post URLs and captions
- Responsive design that works on desktop and mobile

**Log Files**:

- Detailed logging of the scraping process
- Account processing status and results
- Error messages and debugging information
- Timestamps for all operations

## File Naming

Reports and logs are automatically saved with the format:

- HTML reports: `DD-MM-YYYY.html` (e.g., `19-12-2024.html`)
- Log files: `DD-MM-YYYY.log` (e.g., `19-12-2024.log`)

Both files are saved in the "IG Helper" folder on your Desktop by default.

## Project Structure

```bash
instagram-helper/
├── cli.py                  # Command-line interface (main entry point)
├── config.py               # Configuration settings
├── utils.py                # Logging utilities
├── instagram_scraper.py    # Instagram scraping logic
├── report_generator.py     # HTML report generation
├── browser_manager.py      # Browser management
├── templates/              # HTML templates
│   ├── template.html       # Main report template
│   └── test_template.html  # Test template
├── tests/                  # Test suite
│   ├── test_main.py        # Unit tests
│   ├── test_main_integration.py  # Integration tests
│   └── test_utils.py       # Utility tests
├── pyproject.toml         # Project configuration and dependencies
└── README.md              # This file
```

## Dependencies

### Runtime Dependencies

- `playwright` - Browser automation
- `jinja2` - HTML template rendering

### Development Dependencies

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `ruff` - Code formatting and linting
- `mypy` - Static type checking

### Dependency Installation

```bash
# Runtime dependencies only
pip install -e .

# With development dependencies
pip install -e ".[dev]"

# With testing dependencies only
pip install -e ".[test]"
```

## Development

### Available Commands

The project includes a Makefile for common development tasks:

```bash
# Show all available commands
make help

# Install with development dependencies
make setup-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Clean build artifacts
make clean

# Install Playwright browsers
make install-browsers
```

### Code Quality

The project uses several tools to maintain code quality:

- **Ruff**: Code formatting and linting (88 character line length)
- **MyPy**: Static type checking
- **Pytest**: Testing framework

### Testing

Run the test suite:

```bash
pytest
# or
make test
```

Run specific test files:

```bash
pytest tests/test_main.py
pytest tests/test_main_integration.py
pytest tests/test_utils.py
```

Run tests with coverage:

```bash
make test-cov
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
