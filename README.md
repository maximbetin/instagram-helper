# Instagram Helper

A tool that automatically fetches recent posts from specified Instagram accounts and generates a
stylized HTML report with global date sorting and corresponding links.

## Features

- **Automated Scraping**: Fetches recent posts from a configurable list of Instagram accounts.
- **Date Filtering**: Retrieves posts published within a specified number of days.
- **HTML Report Generation**: Creates a clean, responsive HTML report of all fetched posts, sorted chronologically.
- **CLI Interface**: Provides a command-line interface for flexible execution and customization.
- **WSL2 Integration**: Optimized for Windows Subsystem for Linux 2, with support for launching a
  local browser instance.
- **Quality Assured**: Enforced code quality through `ruff`, `mypy`, and a comprehensive `pytest`
  test suite.

## Requirements

- Python 3.12+
- A virtual environment (recommended).
- Access to a Chromium-based browser with remote debugging enabled.

## Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/maximbetin/instagram-helper.git
    cd instagram-helper
    ```

2. **Set Up a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

    For development, install the additional testing and linting tools:

    ```bash
    pip install -r requirements-dev.txt
    ```

## Usage

### Basic Command

To run the scraper with default settings, use the following command:

```bash
python cli.py
```

By default, this will:

- Fetch posts from the last **3 days**.
- Scrape all accounts listed in `config.py`.
- Save the HTML report to the project's root directory.
- Generate a report without opening it in a browser.

### Command-Line Options

You can customize the scraper's behavior using these options:

```text
usage: cli.py [-h] [--days DAYS] [--accounts [ACCOUNTS ...]] [--output OUTPUT] [--log-dir LOG_DIR]

Fetch recent Instagram posts and generate HTML reports.

optional arguments:
  -h, --help            Show this help message and exit
  --days DAYS, -d DAYS  Number of days back to fetch posts from (default: 3).
  --accounts [ACCOUNTS ...], -a [ACCOUNTS ...]
                        Space-separated list of Instagram accounts to fetch from (default: all
                        configured accounts).
  --output OUTPUT, -o OUTPUT
                        Output directory for reports (default: project root).
  --log-dir LOG_DIR     Directory for log files (default: project root).
```

### Examples

- **Fetch posts from the last 7 days**:

  ```bash
  python cli.py --days 7
  ```

- **Scrape specific accounts**:

  ```bash
  python cli.py --accounts gijon biodevas
  ```

- **Save the report to a custom directory**:

  ```bash
  python cli.py --output ./reports
  ```

## Configuration

### Environment Variables

The application can be configured via a `.env` file in the project root. This is the recommended
way to manage settings, especially for browser paths and user data.

- `BROWSER_PATH`: The absolute path to your browser's executable.
- `BROWSER_USER_DATA_DIR`: Path to your browser's user data directory (to reuse sessions).
- `BROWSER_PROFILE_DIR`: The profile directory to use (e.g., "Default" or "Profile 1").
- `BROWSER_DEBUG_PORT`: The remote debugging port.
- `BROWSER_ATTACH_ONLY`: Set to `"true"` to only attach to an existing browser
instance and not launch a new one.

An example `.env` file for WSL2 users targeting a Windows browser:

```env
BROWSER_PATH="/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
BROWSER_USER_DATA_DIR="C:\Users\YourUsername\AppData\Local\BraveSoftware\Brave-Browser\User Data"
BROWSER_PROFILE_DIR="Default"
BROWSER_DEBUG_PORT=9222
```

### Script Configuration

You can also modify `config.py` directly to change:

- `INSTAGRAM_ACCOUNTS`: The default list of accounts to scrape.
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: The maximum number of posts to check per account.
- `TIMEZONE_OFFSET`: The timezone for date localization.

## Development

### Quality Checks

This project uses `ruff` for linting/formatting, `mypy` for static type checking, and `pytest` for testing.

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

All configurations are located in `pyproject.toml` and the `Makefile`.

### Makefile Commands

The `Makefile` provides commands to streamline development:

- `make setup-dev`: Sets up the development environment.
- `make test`: Runs the test suite.
- `make format`: Formats code with `ruff`.
- `make lint`: Lints code with `ruff`.
- `make type-check`: Runs `mypy`.
- `make check-all`: Runs formatting, linting, type checking, and tests.
- `make clean`: Removes build artifacts.

## License

This project is licensed under the MIT License.
