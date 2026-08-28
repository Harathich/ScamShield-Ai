from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Support single key or comma-separated list of keys for automatic rate-limit rotation
_single_key = os.getenv("GROQ_API_KEY", "")
_multi_keys = os.getenv("GROQ_API_KEYS", "")

GROQ_API_KEYS = [k.strip() for k in f"{_single_key},{_multi_keys}".split(",") if k.strip()]
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else None

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MONGO_URI = os.getenv("MONGO_URI")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
