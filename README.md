# Instagram Helper

A GUI-based tool that automatically fetches recent posts from specified Instagram accounts and generates HTML reports with real-time monitoring and configuration options.

## Features

- **GUI Interface**: Tkinter-based interface with real-time monitoring
- **Real-Time Logs**: Monitor scraping progress as it happens
- **Dynamic Configuration**: Adjust settings without editing files
- **Account Management**: Add, remove, or modify Instagram accounts dynamically
- **Progress Tracking**: Visual progress bar and status updates
- **HTML Reports**: Automatically generated reports in your output directory
- **Browser Automation**: Smart browser management with Playwright
- **Code Quality**: Enforced through `ruff`, `mypy`, and comprehensive tests

## Prerequisites

- **Python 3.12+** (strict requirement)
- **Chromium-based browser** (Chrome, Brave, or Edge) with remote debugging enabled
- **WSL2 environment** (Windows Subsystem for Linux 2) - optimized for WSL2

### Browser Setup Requirements

Your browser must support remote debugging. The tool will automatically:

- Launch your browser with `--remote-debugging-port=9222`
- Kill existing browser processes to prevent conflicts
- Handle WSL2-specific path translations
- Provide clear error messages if connection fails

## Getting Started

1. **Setup**:
   - Clone the repository and run `make setup-dev` to prepare the environment.

2. **Configuration**:
   - Create a `.env` file in the project root to configure your browser settings. See the [Environment Variables](#environment-variables) section for details.
   - **Optional**: Customize Instagram accounts directly in the GUI (see [Account Configuration](#instagram-account-configuration)).

3. **Run**:
   - Execute `python run.py` to launch the GUI application.

## Requirements

- Python 3.12+ (strict requirement)
- A virtual environment (recommended)
- Access to a Chromium-based browser with remote debugging enabled
- WSL2 environment (Windows Subsystem for Linux 2)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/maximbetin/instagram-helper.git
   cd instagram-helper
   ```

2. **Set Up the Development Environment**

   Use the provided `Makefile` to simplify setup:

   ```bash
   make setup-dev
   ```

   After setup, activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

## Usage

### Quick Start

Simply run the GUI application:

```bash
python run.py
```

### GUI Features

The Instagram Helper provides a user-friendly interface:

- **Real-Time Monitoring**: Watch scraping progress live with detailed logs
- **Configuration**: Adjust settings without touching configuration files
- **Account Management**: Add, remove, or modify Instagram accounts on the fly
- **Progress Tracking**: See completion status with progress bars and status updates
- **Simple Controls**: Start, stop, and monitor operations with simple buttons
- **Automatic Reports**: HTML reports are generated automatically in your output directory

### How It Works

1. **Launch the GUI**: Run `python run.py`
2. **Configure Settings**: Adjust post age, posts per account, and timeout values
3. **Manage Accounts**: Add or remove Instagram accounts as needed
4. **Start Scraping**: Click "Start Scraping" and monitor progress
5. **Monitor Progress**: Real-time logs show exactly what's happening
6. **Get Results**: HTML reports are automatically saved to your output directory

### Tkinter Requirements

The GUI requires Tkinter, which is usually included with Python. If you encounter issues:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **CentOS/RHEL**: `sudo yum install tkinter`
- **macOS**: Usually included with Python
- **Windows**: Usually included with Python

## Configuration

### Environment Variables

The application can be configured via a `.env` file in the project root.

**Required Variables:**

- `BROWSER_PATH`: The absolute path to your browser's executable.
- `BROWSER_USER_DATA_DIR`: Path to your browser's user data directory (to reuse sessions).

**Optional Variables:**

- `OUTPUT_DIR`: Directory where reports are written (defaults to project root).
- `LOG_DIR`: Directory where logs are stored (defaults to project root).
- `TEMPLATE_PATH`: Path to the Jinja2 HTML template (defaults to "templates/template.html").
- `TIMEZONE_OFFSET`: Numeric hour offset used to localize times in reports (defaults to 2).
- `BROWSER_PROFILE_DIR`: The profile directory to use (defaults to "Default").
- `BROWSER_DEBUG_PORT`: The remote debugging port (defaults to 9222).
- `BROWSER_START_URL`: URL opened when launching a local browser (defaults to Instagram).
- `BROWSER_LOAD_DELAY`: Milliseconds to wait after launching the local browser before connecting (defaults to 5000).
- `BROWSER_CONNECT_SCHEME`: Connection scheme for CDP, usually `http` (defaults to "http").
- `BROWSER_REMOTE_HOST`: Hostname for the browser remote debugger, usually `localhost` (defaults to "localhost").
- `INSTAGRAM_URL`: Base URL for Instagram (defaults to `https://www.instagram.com/`).
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: Maximum posts to process per account (defaults to 5).
- `INSTAGRAM_POST_LOAD_TIMEOUT`: Timeout in ms for loading a post page (defaults to 10000).

An example `.env` file for WSL2 users targeting a Windows browser:

```env
BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
BROWSER_USER_DATA_DIR="C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222
BROWSER_START_URL="https://www.instagram.com/"
BROWSER_LOAD_DELAY=5000
BROWSER_CONNECT_SCHEME="http"
BROWSER_REMOTE_HOST="localhost"
OUTPUT_DIR="/path/to/reports"
LOG_DIR="/path/to/logs"
TEMPLATE_PATH="templates/template.html"
TIMEZONE_OFFSET=2
INSTAGRAM_URL="https://www.instagram.com/"
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=5
INSTAGRAM_POST_LOAD_TIMEOUT=10000
```

### Instagram Account Configuration

The tool comes pre-configured with **50 Instagram accounts** including:

- `agendagijon`, `biodevas`, `centroniemeyer`, `aytoviedo`, `aytocastrillon`
- `bibliotecasdegijonxixon`, `conectaoviedo`, `conocerasturias`, `cultura.gijon`
- And many more cultural and institutional accounts

**Customization**: You can modify accounts directly in the GUI:

1. **GUI Input (Recommended)**: Use the "Accounts" section in the GUI:
   - Enter one Instagram account per line in the text area
   - Accounts are automatically loaded when you start the application
   - Changes take effect immediately when you start scraping

2. **Code Configuration**: Modify `config.py` to:
   - Adjust `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` (default: 5 posts per account)
   - Change `INSTAGRAM_POST_LOAD_TIMEOUT` (default: 10 seconds per post)

**Note**: The GUI text area provides a simple way to manage accounts without editing external files.

## Troubleshooting

### Browser Connection Issues

- **Remote debugging not enabled**: Ensure your browser supports remote debugging
- **Invalid browser path**: Check that `BROWSER_PATH` points to a valid executable
- **User data directory inaccessible**: Verify `BROWSER_USER_DATA_DIR` exists and is writable
- **Port conflicts**: Ensure port 9222 is not blocked or in use by another process
- **ECONNREFUSED errors**: Close any existing browser instances before running the tool

### WSL2 Path Issues

- **Browser paths**: Use Windows-style paths for browser directories: `C:\Users\...`
- **Output paths**: Use Linux-style paths for output: `/mnt/c/Users/...`
- **Path translation**: The tool handles WSL2 path conversions automatically

### Instagram Scraping Issues

- **HTML structure changes**: Instagram frequently updates their page structure, which may break the tool
- **Rate limiting**: Reduce `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` if experiencing blocked requests
- **Authentication issues**: The tool relies on browser session cookies; clear browser data if needed
- **Selector failures**: If posts aren't being detected, Instagram may have changed their HTML

### Common Error Messages

- **"BROWSER_PATH environment variable is not set"**: Add `BROWSER_PATH` to your `.env` file
- **"Connection refused to browser"**: Close any existing browser instances and try again
- **"No post links found"**: Instagram may have changed their page structure
- **"Timeout loading post"**: Increase `INSTAGRAM_POST_LOAD_TIMEOUT` in your `.env` file

## Important Notes

**CRITICAL**: Do not modify the caption selectors in `instagram_scraper.py`. These selectors are fragile and changes will break the tool's functionality.

**Instagram Dependencies**: The tool's success depends on Instagram's HTML structure remaining consistent. The tool may need updates if Instagram makes significant changes to their pages.

**Rate Limiting**: Instagram may block requests if too many are made too quickly. The default settings are conservative to avoid this.

**WSL2 Optimization**: This tool is specifically designed for Windows Subsystem for Linux 2 environments and may not work optimally in other setups.

**Browser Management**: The tool always launches a new browser instance to ensure reliable operation. If you encounter connection errors, close any existing browser instances and try again.

**Account Management**: Instagram accounts are now managed directly through the GUI text area, making it easier to customize without editing external files.

## Development

### Quality Checks

This project uses `ruff` (linting/formatting), `mypy` (static type checking), and `pytest` (tests).

- **Run all checks**:

  ```bash
  make check-all
  ```

- **Format code**:

  ```bash
  make format
  ```

- **Run tests**:

  ```bash
  make test
  ```

Configurations live in `pyproject.toml` and are executed via the `Makefile`.

### Makefile Commands

The `Makefile` provides commands to streamline development:

- `make setup-dev`: Sets up the development environment
- `make test`: Runs the test suite
- `make format`: Formats code with `ruff`
- `make lint`: Lints code with `ruff`
- `make type-check`: Runs `mypy`
- `make check-all`: Runs formatting, linting, type checking, and tests
- `make clean`: Removes build artifacts

### Common Development Workflows

```bash
# Setup and activate environment
make setup-dev
source venv/bin/activate

# Run quality checks before committing
make check-all

# Test with custom parameters
python run.py

# Run specific test files
./venv/bin/pytest tests/test_instagram_scraper.py -v
```

## License

This project is licensed under the MIT License.
