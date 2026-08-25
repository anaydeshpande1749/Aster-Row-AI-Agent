import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base"
ORDERS_FILE = BASE_DIR / "data" / "orders.json"
VECTOR_DB_DIR = BASE_DIR / "storage" / "chroma"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")