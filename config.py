from typing import List

# Instagram accounts to track
INSTAGRAM_ACCOUNTS: List[str] = [
    "aytoviedo",
]

# How far back to look for posts (in days)
DAYS_TO_LOOK_BACK: int = 7

# Fetcher configuration
MAX_RETRIES: int = 3
RETRY_DELAY: int = 10  # seconds
POSTS_PER_ACCOUNT: int = 5
ACCOUNT_DELAY: int = 10  # seconds
