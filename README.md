# Instagram Updates Tracker

A simple Python application that tracks recent posts from specified Instagram accounts and displays new posts in a human-readable format.

## Features

- Tracks posts from specified Instagram accounts
- Shows posts from the last 7 days
- Displays post URLs, dates, and captions
- Keeps track of previously seen posts
- Clean and readable output format

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
- Display any new posts that weren't seen in previous runs
- Store the post history for future reference

## Configuration

Edit `config.py` to:
- Add or remove Instagram accounts to track
- Modify the number of days to look back
- Change the data storage location

## Notes

- The application uses the `instaloader` library to fetch Instagram data
- Authentication is recommended to avoid rate limiting
- Post history is stored in the `data` directory
- Be mindful of Instagram's rate limits and terms of service
