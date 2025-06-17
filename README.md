# Instagram Post Fetcher

A tool that opens Instagram for manual login, then automatically fetches recent posts from specified accounts.

## Features

- **Manual login**: Opens Instagram for you to log in manually
- **Automatic fetching**: After login, fetches posts from specified accounts
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
- After you press Enter, start fetching posts from specified accounts
- Display a summary of fetched posts
- Wait for you to press Enter again to close

## Configuration

Edit `config.py` to modify:
- `INSTAGRAM_ACCOUNTS`: List of Instagram usernames to fetch posts from
- `POSTS_PER_ACCOUNT`: Number of posts to fetch per account (default: 5)
- `DELAY_BETWEEN_ACCOUNTS`: Delay between checking accounts in seconds (default: 3)
- `BROWSER_VIEWPORT`: Browser window size
- `USER_AGENT`: Browser user agent string

## Files

- `main.py` - Entry point with login and post fetching logic
- `config.py` - Configuration settings
- `utils.py` - Logging utilities

## Notes

This tool requires manual login to access Instagram content. After logging in, it will automatically fetch recent posts from the specified accounts. The browser remains open throughout the process for transparency and debugging.
