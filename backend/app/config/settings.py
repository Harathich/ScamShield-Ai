from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Default to llama-3.1-8b-instant or llama-3.3-70b-versatile if not specified
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

MONGO_URI = os.getenv("MONGO_URI")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
