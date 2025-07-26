import os

PROCESSED_URLS_FILE = "processed_urls.txt"

def load_processed_urls() -> set:
    """Loads the set of already processed URLs from a file."""
    if not os.path.exists(PROCESSED_URLS_FILE):
        return set()
    with open(PROCESSED_URLS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_processed_url(url: str):
    """Appends a new URL to the processed URLs file."""
    with open(PROCESSED_URLS_FILE, "a") as f:
        f.write(url + "\n")

