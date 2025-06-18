# Instagram Posts Fetcher

A tool that opens Instagram for manual login, then automatically fetches recent posts from specified accounts and generates a stylized HTML report with global date sorting and corresponding links.

## Features

- **Manual login**: Opens Instagram for you to log in manually
- **Automatic fetching**: After login, fetches posts from specified accounts
- **Date filtering**: Only fetches posts from the last few days (configurable)
- **Global post sorting**: All posts sorted by published date (newest first) regardless of account
- **HTML report generation**: Creates a stylized, responsive HTML report with all fetched posts
- **Clean link copying**: One-click copy of clean Instagram URLs without tracking parameters
- **Desktop integration**: Automatically saves reports to Desktop with date-based naming
- **Auto-browser opening**: Automatically opens the generated HTML report in your default browser
- **Text-focused**: Captures post captions and dates (image fetching disabled for performance)
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
- Generate a stylized HTML report on your Desktop (`instagram_updates_YYYYMMDD.html`)
- Automatically close the browser
- Open the HTML report in your default browser

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
2. **HTML Report**: A stylized, responsive HTML file saved to Desktop containing:
- Summary statistics
- All posts sorted globally by date (newest first)
- Post cards with captions, dates, and account information
- Direct links to original Instagram posts
- Clean copy buttons for sharing links without tracking parameters
- Responsive design that works on mobile and desktop

## File Naming

Reports are automatically saved to your Desktop folder with the format:
- `instagram_updates_YYYYMMDD.html` (e.g., `instagram_updates_20241220.html`)

## Files

- `main.py` - Main script with login, post fetching, HTML generation, and browser automation
- `config.py` - Configuration settings for accounts, browser, and fetching behavior
- `utils.py` - Logging utilities and shared functions
- `requirements.txt` - Python dependencies (Playwright)

## Key Features

### Global Post Sorting
- All posts from all accounts are sorted by published date
- Newest posts appear first regardless of which account posted them
- Provides a unified timeline view of recent activity

### Clean Link Sharing
- Each post has a "📋 Copy Link" button
- Copies clean Instagram URLs without tracking parameters or query strings
- Perfect for sharing in WhatsApp, Telegram, or other messaging apps
- Visual feedback shows when link is successfully copied

### Desktop Integration
- Reports automatically save to your Desktop folder
- Cross-platform support (Windows, macOS, Linux)
- Date-based naming for easy organization
- Automatic browser opening after generation

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.