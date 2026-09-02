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
# TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
# TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
# TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "vacancies_parser")

# --- Telegram scraping settings (no auth needed) ---
TELEGRAM_BASE_URL = "https://t.me/s"
TELEGRAM_CHANNELS = [
    "zarubezhom_jobs",
    "dev_connectablejobs",
    "remotejun",
    "Remoteit",
    "evacuatejobs",
    "young_june",
]

# --- hh.ru search settings ---
HH_SEARCH_KEYWORDS = [
    "Python developer",
    "Data Analyst",
    "Data Engineer",
    "LLM AI Engineer",
]
HH_PER_PAGE = 50          # max 100 per hh.ru API
HH_ONLY_REMOTE = True     # filter: schedule=remote
