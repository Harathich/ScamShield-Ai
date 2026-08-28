import os
from pathlib import Path
from dotenv import dotenv_values

candidates = [
    Path.cwd() / ".env",
    Path.cwd().parent / ".env",
    Path(r"A:\Capstone\ScamShieldAI\.env"),
    Path(r"A:\Capstone\ScamShieldAI\backend\.env"),
]

for p in candidates:
    if p.exists():
        print(f"FOUND: {p}")
        vals = dotenv_values(p)
        model = vals.get("GROQ_MODEL", "(not set)")
        key = vals.get("GROQ_API_KEY", "(not set)")
        key_preview = key[:10] + "..." if len(key) > 10 else key
        print(f"  GROQ_MODEL = {model}")
        print(f"  GROQ_API_KEY = {key_preview}")
    else:
        print(f"NOT FOUND: {p}")
