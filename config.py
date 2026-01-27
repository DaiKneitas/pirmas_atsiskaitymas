import os
from dotenv import load_dotenv

# --- Library rules ---
MAX_BOOKS_PER_READER = 3
DEFAULT_LOAN_DAYS = 30


# Load variables from .env into environment
load_dotenv()

# --- db user and password (read from env) ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "biblioteka2")

# check if .env file exists
if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD is empty. Create a .env file and set DB_PASSWORD. Example is in .env.example file")
