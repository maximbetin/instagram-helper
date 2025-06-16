from pathlib import Path

# Base directory for storing data
BASE_DIR = Path(__file__).parent / "data"

# Instagram accounts to track
INSTAGRAM_ACCOUNTS = [
    "aytoviedo",
]

# How far back to look for posts
DAYS_TO_LOOK_BACK = 7

# File to store the last run timestamp
LAST_RUN_FILE = BASE_DIR / "last_run.txt"

# File to store post history
POSTS_HISTORY_FILE = BASE_DIR / "posts_history.json"

# Create data directory if it doesn't exist
BASE_DIR.mkdir(exist_ok=True)
