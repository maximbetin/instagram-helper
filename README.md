[![Run Tests](https://github.com/maximbetin/instagram-updates/actions/workflows/test.yml/badge.svg)](https://github.com/maximbetin/instagram-updates/actions/workflows/test.yml)

# Instagram Updates

A tool that automatically fetches recent posts from specified accounts and generates a stylized HTML report with global date sorting and corresponding links.

## Features

- **Automatic fetching**: Fetches posts from specified accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts

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
- Open a Brave browser window (configurable)
- Navigate to Instagram's main page
- Start fetching posts from specified accounts
- Display progress in the console
- Generate a stylized HTML report on your Desktop

## Configuration

Edit `config.py` to modify:

### Post Fetching Settings
- `INSTAGRAM_MAX_POST_AGE`: Number of days back to fetch posts from (default: 3)
- `INSTAGRAM_MAX_POSTS_PER_ACCOUNT`: Maximum posts to check per account (default: 3)
- `BROWSER_LOAD_DELAY`: Delay between page loads in seconds (default: 3)

### Instagram Accounts
- `INSTAGRAM_ACCOUNTS`: List of Instagram usernames to fetch posts from

### Browser Settings
- `BROWSER_PATH`: Path to browser executable (default: Brave browser)
- `BROWSER_DEBUG_PORT`: Debug port for browser connection (default: 9222)
- `BROWSER_LOAD_TIMEOUT`: Page load timeout in milliseconds (default: 10000)
- `TIMEZONE`: Timezone for date processing (default: Europe/Madrid UTC+2)

## Output

The tool generates an HTML report:

- Summary statistics (total accounts checked, total posts found)
- All posts with captions, dates, and account information
- Direct links to original Instagram posts

## File Naming

Reports are automatically saved to your Desktop folder with the format:
- `instagram_updates_DDMMYYYY.html` (e.g., `instagram_updates_19062025.html`)

## Files

- `main.py` - Main script with browser automation, post fetching, and HTML report generation
- `config.py` - Configuration settings for accounts, browser, and fetching behavior
- `utils.py` - Logging utilities and shared functions
- `template.html` - HTML template for report generation
- `requirements.txt` - Python dependencies

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
