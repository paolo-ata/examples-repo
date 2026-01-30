import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROGRESS_FILE = BASE_DIR / "progress.json"

CASE_BIBLES_FILE = DATA_DIR / "case_bibles.json"

DEFAULT_MODEL = "gpt-5-mini"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

MAX_TOKENS = 8000
TEMPERATURE = 0.7
DELAY_BETWEEN_CALLS = 0.5
