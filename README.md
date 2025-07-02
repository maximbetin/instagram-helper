[![Run Tests](https://github.com/maximbetin/instagram-updates/actions/workflows/ci.yml/badge.svg)](https://github.com/maximbetin/instagram-updates/actions/workflows/ci.yml)

# Instagram Updates

A tool that automatically fetches recent posts from specified Instagram accounts and generates a stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified Instagram accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Global date sorting**: All posts are sorted by date across all accounts (newest first)
- **Interactive report**: HTML report includes copy-to-clipboard functionality for post links and captions
- **Progress tracking**: Real-time console output showing processing progress
- **CLI interface**: Command-line options for flexible usage
- **Environment configuration**: Support for environment variables

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

**Note:** The tool is configured to use Brave browser by default. If you don't have Brave installed, you can change the browser path in `config.py` or set the `BROWSER_PATH` environment variable.

## Usage

### Basic Usage

1. Run the script with default settings:
```bash
python main.py
```

2. Or use the CLI interface for more options:
```bash
python cli.py
```

3. Or install the package and use the command-line tool:
```bash
pip install -e .
instagram-updates
```

**Default Behavior:**
- Fetches posts from the last 3 days
- Processes all configured Instagram accounts
- Saves HTML reports and logs to `Desktop/IG Updates/`
- Automatically opens the generated report

### CLI Options

```bash
python cli.py [OPTIONS]

Options:
  --days, -d INT          Number of days back to fetch posts from (default: 1)
  --accounts, -a TEXT...  Specific Instagram accounts to fetch from
  --output, -o PATH       Output directory for reports (default: Desktop/IG Updates)
  --log-dir PATH          Directory for log files (default: Desktop/IG Updates)
  --no-open               Do not automatically open the generated report
  --verbose, -v           Enable verbose logging
  --help                  Show this message and exit
```

### Examples

```bash
# Use default settings (saves to Desktop/IG Updates folder)
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
export BROWSER_LOAD_DELAY=2
export BROWSER_LOAD_TIMEOUT=10000
export BROWSER_PATH="/path/to/browser"

# Instagram settings
export INSTAGRAM_MAX_POST_AGE=3
export INSTAGRAM_MAX_POSTS_PER_ACCOUNT=3
export INSTAGRAM_URL="https://www.instagram.com/"

# Output settings
export OUTPUT_DIR="/path/to/output"
export LOG_DIR="/path/to/logs"
export TIMEZONE_OFFSET=2
```

### Configuration File

Edit `config.py` to modify:

- **Post Fetching Settings**: Days back to fetch (default: 3), max posts per account (default: 3), load delays
- **Instagram Accounts**: List of usernames to fetch posts from (currently configured for Asturias cultural accounts)
- **Browser Settings**: Browser path (default: Brave), debug port, timeouts
- **Output Settings**: Output and log directories (default: Desktop/IG Updates)

## Output

The tool generates an interactive HTML report and detailed logs:

**HTML Report:**
- Summary statistics (total accounts checked, total posts found, date range)
- All posts sorted by date (newest first) with captions, dates, and account information
- Direct links to original Instagram posts
- Copy-to-clipboard buttons for post URLs and captions
- Responsive design that works on desktop and mobile

**Log Files:**
- Detailed logging of the scraping process
- Account processing status and results
- Error messages and debugging information
- Timestamps for all operations

## File Naming

Reports and logs are automatically saved with the format:
- HTML reports: `DD-MM-YYYY.html` (e.g., `19-12-2024.html`)
- Log files: `DD-MM-YYYY.log` (e.g., `19-12-2024.log`)

Both files are saved in the "IG Updates" folder on your Desktop by default.

## Project Structure

```
instagram-updates/
├── main.py                 # Main script (legacy entry point)
├── cli.py                  # Command-line interface
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
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Dependencies

- `playwright` - Browser automation
- `jinja2` - HTML template rendering
- `pytest` - Testing framework (for development)

## Testing

Run the test suite:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/test_main.py
pytest tests/test_main_integration.py
pytest tests/test_utils.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
