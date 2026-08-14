import os
from pathlib import Path
from dotenv import load_dotenv

# The path to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Loading variables from .env
load_dotenv(BASE_DIR / ".env")

# --- Database ---
DB_PATH = BASE_DIR / "data" / "vacancies.db"

# --- hh.ru API ---
HH_API_BASE_URL = "https://api.hh.ru"

# --- Telegram API ---
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "vacancies_parser")

# List of channels for parsing
TELEGRAM_CHANNELS = [
    # "@example_channel",
]
