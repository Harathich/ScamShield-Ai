from dotenv import load_dotenv
import os
from pathlib import Path

# Automatically search for .env in current working dir, backend/, and project root
_curr_dir = Path.cwd()
_backend_dir = Path(__file__).resolve().parent.parent.parent
_root_dir = _backend_dir.parent

for possible_path in [_curr_dir / ".env", _backend_dir / ".env", _root_dir / ".env"]:
    if possible_path.exists():
        load_dotenv(dotenv_path=possible_path, override=True)
        break
else:
    load_dotenv()

# Support single key or comma-separated list of keys for automatic rate-limit rotation
_single_key = os.getenv("GROQ_API_KEY", "")
_multi_keys = os.getenv("GROQ_API_KEYS", "")

GROQ_API_KEYS = [k.strip() for k in f"{_single_key},{_multi_keys}".split(",") if k.strip()]
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else None

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MONGO_URI = os.getenv("MONGO_URI")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
