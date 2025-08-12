# Instagram Helper

A tool that automatically fetches recent posts from specified Instagram accounts and generates a
stylized HTML report with global date sorting and corresponding links.

## Features

- **Automated Scraping**: Fetches recent posts from a configurable list of Instagram accounts.
- **Date Filtering**: Retrieves posts published within a specified number of days.
- **HTML Report Generation**: Creates a clean, responsive HTML report of all fetched posts, sorted
  chronologically.
- **CLI Interface**: Provides a command-line interface for flexible execution and customization.
- **WSL2 Integration**: Optimized for Windows Subsystem for Linux 2, with support for launching a
  local browser instance.
- **Quality Assured**: Enforced code quality through `ruff`, `mypy`, and a comprehensive `pytest`
  test suite.

## Prerequisites

- **Python 3.12+** (strict requirement - the tool will not work with older versions)
- **Chromium-based browser** (like Chrome, Brave, or Edge) with remote debugging enabled
- **WSL2 environment** (Windows Subsystem for Linux 2) - this tool is specifically optimized for
  WSL2

### Browser Setup Requirements

Your browser must support remote debugging. The tool will automatically:

- Launch your browser with `--remote-debugging-port=9222`
- Kill existing browser processes to prevent conflicts
- Handle WSL2-specific path translations
- Provide clear error messages if connection fails (e.g., ECONNREFUSED)

## Getting Started

To get started with the Instagram Helper, follow these steps:

1. **Setup**:

   - Clone the repository and run `make setup-dev` to prepare the environment.

2. **Configuration**:

   - Create a `.env` file in the project root to configure your browser settings. See the
     [Environment Variables](#environment-variables) section for details.

3. **Run**:
   - Execute `python cli.py --help` to see the available commands and options.

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

   We recommend using the provided `Makefile` to simplify setup. This command creates a virtual
   environment and installs all required dependencies.

   ```bash
   make setup-dev
   ```

   After setup, activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

## Usage

### Basic Command

To run the scraper with default settings, use the following command:

```bash
python cli.py
```

By default, this will:

- Fetch posts from the last **3 days**
- Scrape all accounts listed in `config.py`
- Save the HTML report to the project's root directory
- Generate a report without opening it in a browser

### Command-Line Options

You can customize the scraper's behavior using these options:

```text
usage: cli.py [-h] [--days DAYS] [--accounts [ACCOUNTS ...]] [--output OUTPUT]
              [--log-dir LOG_DIR] [--headless]

Fetch recent Instagram posts and generate HTML reports.

options:
  -h, --help            show this help message and exit
  --days DAYS, -d DAYS  Number of days back to fetch posts from (default: 3)
  --accounts [ACCOUNTS ...], -a [ACCOUNTS ...]
                        Specific Instagram accounts to fetch from (default: all
                        configured accounts)
  --output OUTPUT, -o OUTPUT
                        Output directory for reports (default:
                        /home/maxim/instagram-helper)
  --log-dir LOG_DIR     Directory for log files (default: /home/maxim/instagram-
                        helper)
  --headless            Run the browser in headless mode (no GUI).
```

### Examples

- **Fetch posts from the last 7 days**:

  ```bash
  python cli.py --days 7
  ```

- **Scrape specific accounts**:

  ```bash
  python cli.py --accounts aytoviedo biodevas
  ```

- **Save the report to a custom directory**:

  ```bash
  python cli.py --output ./reports
  ```

## Configuration

### Environment Variables

The application can be configured via a `.env` file in the project root. This is the recommended way
to manage settings, especially for browser paths and user data.

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
- `BROWSER_LOAD_DELAY`: Milliseconds to wait after launching the local browser before connecting
  (defaults to 5000).
- `BROWSER_CONNECT_SCHEME`: Connection scheme for CDP, usually `http` (defaults to "http").
- `BROWSER_REMOTE_HOST`: Hostname for the browser remote debugger, usually `localhost` (defaults to
  "localhost").
- `INSTAGRAM_URL`: Base URL for Instagram (defaults to "<https://www.instagram.com/>").
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: Maximum posts to process per account (defaults to 3).
- `INSTAGRAM_POST_LOAD_TIMEOUT`: Timeout in ms for loading a post page (defaults to 20000).

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
INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3
INSTAGRAM_POST_LOAD_TIMEOUT=20000
```

### Instagram Account Configuration

The tool comes pre-configured with 25+ Instagram accounts including:

- `agendagijon`, `biodevas`, `centroniemeyer`, `aytoviedo`, `aytocastrillon`
- `bibliotecasdegijonxixon`, `conectaoviedo`, `conocerasturias`, `cultura.gijon`

**Customization**: You can modify `config.py` to:

- Add or remove Instagram accounts from the `INSTAGRAM_ACCOUNTS` list
- Adjust `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` (default: 3 posts per account)
- Change `INSTAGRAM_POST_LOAD_TIMEOUT` (default: 20 seconds per post)

### Script Configuration

You can also modify `config.py` directly to change:

- `INSTAGRAM_ACCOUNTS`: The default list of accounts to scrape.
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: The maximum number of posts to check per account (default: 3).
- `TIMEZONE_OFFSET`: The timezone for date localization.

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

- **HTML structure changes**: Instagram frequently updates their page structure, which may break the
  tool
- **Rate limiting**: Reduce `INSTAGRAM_MAX_POSTS_PER_ACCOUNT` if experiencing blocked requests
- **Authentication issues**: The tool relies on browser session cookies; clear browser data if
  needed
- **Selector failures**: If posts aren't being detected, Instagram may have changed their HTML

### Common Error Messages

- **"BROWSER_PATH environment variable is not set"**: Add `BROWSER_PATH` to your `.env` file
- **"Connection refused to browser"**: Close any existing browser instances and try again
- **"No post links found"**: Instagram may have changed their page structure
- **"Timeout loading post"**: Increase `INSTAGRAM_POST_LOAD_TIMEOUT` in your `.env` file

## Important Notes

**CRITICAL**: Do not modify the caption selectors in `instagram_scraper.py`. These selectors are
fragile and changes will break the tool's functionality.

**Instagram Dependencies**: The tool's success depends on Instagram's HTML structure remaining
consistent. The tool may need updates if Instagram makes significant changes to their pages.

**Rate Limiting**: Instagram may block requests if too many are made too quickly. The default
settings are conservative to avoid this.

**WSL2 Optimization**: This tool is specifically designed for Windows Subsystem for Linux 2
environments and may not work optimally in other setups.

**Browser Management**: The tool always launches a new browser instance to ensure reliable
operation. If you encounter connection errors, close any existing browser instances and try again.

## Development

### Quality Checks

This project uses only `ruff` (linting/formatting), `mypy` (static type checking), and `pytest`
(tests).

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
python cli.py --days 7 --accounts aytoviedo biodevas

# Run specific test files
./venv/bin/pytest tests/test_instagram_scraper.py -v
```

## License

This project is licensed under the MIT License.
