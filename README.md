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

### Quick Setup for WSL2 Users

If you're running from WSL2 and want to use Windows Brave browser:

```bash
# 1. Launch Windows Brave with remote debugging
./scripts/launch_brave_wsl2.sh

# 2. Run the Instagram Helper
python cli.py
```

The tool automatically detects WSL2 and connects to your Windows Brave instance with your existing
profile (cookies, sessions, etc.).

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

## Configuration

### Environment Variables

You can configure the tool using environment variables:

```bash
# Browser settings
export BROWSER_DEBUG_PORT=9222
export BROWSER_LOAD_DELAY=5000     # milliseconds
export BROWSER_LOAD_TIMEOUT=15000  # milliseconds
export BROWSER_PATH="/usr/bin/brave-browser"  # Or any Chromium-based browser

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

### WSL2 Support

The tool automatically detects when running in WSL2 and adapts to use Windows Brave browser with
your existing user profile (cookies, sessions, etc.).

#### Automatic WSL2 Detection

The tool automatically detects WSL2 environment and configures itself accordingly:

- Detects WSL2 by checking `/proc/version` for "microsoft"
- Automatically finds Windows host IP from `/etc/resolv.conf`
- Switches to Windows Brave paths when in WSL2 mode

#### WSL2 Configuration

```bash
# WSL2-specific environment variables (auto-detected, but can be overridden)
export WSL2_MODE=auto                    # Set to "disabled" to force Linux mode
export WSL_HOST_IP=172.27.48.1          # Auto-detected from /etc/resolv.conf
export BROWSER_PATH="/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
```

#### Manual WSL2 Setup

If you prefer to manually launch Brave with remote debugging:

#### Option 1: From WSL2 (Recommended)

```bash
# Launch Windows Brave with remote debugging
./scripts/launch_brave_wsl2.sh

# Or with custom port/URL
./scripts/launch_brave_wsl2.sh -p 9223 -u https://www.instagram.com/
```

#### Option 2: From Windows

```cmd
# Run from Windows Command Prompt or PowerShell
scripts\launch_brave_wsl2.bat

# Or with custom port/URL
scripts\launch_brave_wsl2.bat -p 9223 -u https://www.instagram.com/
```

#### Option 3: Manual Launch

```bash
# From WSL2, launch Windows Brave with debugging
/mnt/c/Program\ Files/BraveSoftware/Brave-Browser/Application/brave.exe \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  https://www.instagram.com/ &
```

#### Testing and Verification

Test your WSL2 setup with these helper scripts:

```bash
# Test WSL2 detection and configuration
python scripts/test_wsl2_detection.py

# See WSL2 integration demo
python scripts/demo_wsl2.py
```

#### WSL2 Security Notes

- The debugging port is exposed on your Windows host network
- Consider using Windows Firewall to restrict access to localhost and WSL2 IPs only
- Only use on trusted networks

#### Troubleshooting WSL2

**Connection refused errors:**

- Ensure Brave is running with `--remote-debugging-port=9222 --remote-debugging-address=0.0.0.0`
- Check Windows Firewall isn't blocking port 9222
- Verify the Windows host IP is correct (check `/etc/resolv.conf` in WSL2)

**Profile mismatch:**

- Don't use custom `--user-data-dir` unless you want a separate profile
- The tool uses your normal Windows Brave profile by default

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
├── scripts/                # Helper scripts
│   ├── launch_brave_wsl2.sh    # WSL2 Brave launcher (Linux)
│   ├── launch_brave_wsl2.bat   # WSL2 Brave launcher (Windows)
│   ├── test_wsl2_detection.py  # WSL2 configuration test
│   └── demo_wsl2.py            # WSL2 integration demo
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
