# Instagram Updates Tracker

A simple Python application that displays recent posts from specified Instagram accounts in a human-readable format.

## Features

- Shows posts from specified Instagram accounts
- Displays posts from the last specified number of days
- Shows post URLs, dates, and captions
- Clean and readable output format

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate # On Linux/macOS: source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Authentication

To avoid rate limiting and access restrictions, you should authenticate with Instagram:

1. Set up environment variables for your Instagram credentials:
```bash
# On Windows PowerShell:
$env:INSTAGRAM_USERNAME="your_username"
$env:INSTAGRAM_PASSWORD="your_password"

# On Windows Command Prompt:
set INSTAGRAM_USERNAME=your_username
set INSTAGRAM_PASSWORD=your_password

# On Linux/macOS:
export INSTAGRAM_USERNAME="your_username"
export INSTAGRAM_PASSWORD="your_password"
```

2. For security, you can create a `.env` file in the project root and add it to `.gitignore`:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```
Then install python-dotenv and load it in your script.

Note: Using your Instagram credentials is optional but recommended to avoid rate limiting.

## Usage

1. Configure the accounts to track in `config.py`
2. Run the script:
```bash
python main.py
```

The script will:
- Fetch recent posts from the configured accounts
- Display posts from the last 7 days

## Configuration

Edit `config.py` to:
- Add or remove Instagram accounts to track
- Modify the number of days to look back

## Notes

- The application uses the `instaloader` library to fetch Instagram data
- Authentication is recommended to avoid rate limiting
- Be mindful of Instagram's rate limits and terms of service
