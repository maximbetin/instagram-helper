# Instagram Posts Fetcher

A tool that opens Instagram for manual login, then automatically fetches recent posts from specified accounts and generates a stylized HTML report.

## Features

- **Manual login**: Opens Instagram for you to log in manually
- **Automatic fetching**: After login, fetches posts from specified accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Image extraction**: Captures post images and captions
- **Clean interface**: Simple, focused functionality
- **Configurable**: Easy to modify account list and settings

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
- Open a Chrome browser window
- Navigate to Instagram's main page
- Wait for you to log in manually
- After you press Enter, verify your login status
- Start fetching posts from specified accounts
- Display a summary of fetched posts in the console
- Generate a stylized HTML report (`instagram_posts.html`)
- Wait for you to press Enter again to close

## Configuration

Edit `config.py` to modify:

### Post Fetching Settings
- `DAYS_BACK_TO_FETCH`: Number of days back to fetch posts from (default: 3)
- `MAX_POSTS_TO_CHECK`: Maximum posts to check per account before giving up (default: 5)
- `DELAY_BETWEEN_ACCOUNTS`: Delay between checking accounts in seconds (default: 3)

### Instagram Accounts
- `INSTAGRAM_ACCOUNTS`: List of Instagram usernames to fetch posts from
- Currently configured with Asturias-focused accounts (cultural venues, events, tourism)

### Browser Settings
- `BROWSER_VIEWPORT`: Browser window size (default: 1366x768)
- `USER_AGENT`: Browser user agent string
- `LOCALE`: Browser locale (default: 'en-US')
- `TIMEZONE`: Browser timezone (default: 'Europe/Madrid')

## Output

The tool generates two types of output:

1. **Console Summary**: Shows statistics and basic information about fetched posts
2. **HTML Report**: A stylized, responsive HTML file (`instagram_posts.html`) containing:
- Summary statistics
- Post cards with images, captions, and dates
- Direct links to original Instagram posts
- Organized by account

## Files

- `main.py` - Main script with login, post fetching, and HTML generation logic
- `config.py` - Configuration settings for accounts, browser, and fetching behavior
- `utils.py` - Logging utilities and shared functions
- `requirements.txt` - Python dependencies (Playwright)

## Notes

- This tool requires manual login to access Instagram content
- After logging in, it will automatically fetch recent posts from the specified accounts
- The browser remains open throughout the process for transparency and debugging
- The HTML report is self-contained and can be opened in any web browser
- Posts are filtered by date to only show recent content
- The tool is currently configured for Asturias (Spain) cultural and event accounts

## Known Issues

- Sometimes the image is not extracted / displayed properly in the HTML report.
- Some posts captions or descriptions are not extracted / displayed properly in the HTML report.
- No need to keep the browser open after the script finishes.
- Would be nice to collapse updates per account in the HTML report.
- Even better would be to have the most recent posts displayed first, regardless of the account.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.