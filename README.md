[![Run Tests](https://github.com/maximbetin/instagram-updates/actions/workflows/test.yml/badge.svg)](https://github.com/maximbetin/instagram-updates/actions/workflows/test.yml)

# Instagram Updates

A tool that automatically fetches recent posts from specified Instagram accounts and generates a stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified Instagram accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Global date sorting**: All posts are sorted by date across all accounts (newest first)
- **Interactive report**: HTML report includes copy-to-clipboard functionality for post links and captions
- **Progress tracking**: Real-time console output showing processing progress

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

1. Run the script:
```bash
python main.py
```

2. The script will:
- Launch a Brave browser instance with remote debugging
- Navigate to Instagram's main page
- Process each configured account to fetch recent posts
- Display progress in the console
- Generate a stylized HTML report on your Desktop
- Automatically open the generated report

## Configuration

Edit `config.py` to modify:

### Post Fetching Settings
- `INSTAGRAM_MAX_POST_AGE`: Number of days back to fetch posts from (default: 3)
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: Maximum posts to check per account (default: 5)
- `BROWSER_LOAD_DELAY`: Delay between page loads in seconds (default: 5)

### Instagram Accounts
- `INSTAGRAM_ACCOUNTS`: List of Instagram usernames to fetch posts from (currently configured for Asturias cultural accounts)

### Browser Settings
- `BROWSER_PATH`: Path to browser executable (default: Brave browser on Windows)
- `BROWSER_DEBUG_PORT`: Debug port for browser connection (default: 9222)
- `BROWSER_LOAD_TIMEOUT`: Page load timeout in milliseconds (default: 10000)
- `TIMEZONE`: Timezone for date processing (default: UTC+2)

## Output

The tool generates an interactive HTML report with:

- Summary statistics (total accounts checked, total posts found, date range)
- All posts sorted by date (newest first) with captions, dates, and account information
- Direct links to original Instagram posts
- Copy-to-clipboard buttons for post URLs and captions
- Responsive design that works on desktop and mobile

## File Naming

Reports are automatically saved to your Desktop folder with the format:
- `instagram_updates_YYYYMMDD.html` (e.g., `instagram_updates_20241219.html`)

## Project Structure

- `main.py` - Main script with browser automation, post fetching, and HTML report generation
- `config.py` - Configuration settings for accounts, browser, and fetching behavior
- `utils.py` - Logging utilities and shared functions
- `template.html` - HTML template for report generation with interactive features
- `requirements.txt` - Python dependencies
- `tests/` - Test suite with unit tests for main functionality

## Dependencies

- `playwright` - Browser automation
- `jinja2` - HTML template rendering
- `pytest` - Testing framework (for development)

## Testing

Run the test suite:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
