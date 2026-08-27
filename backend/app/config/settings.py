from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Leave the model unset unless it is explicitly configured. LLMService selects
# a compatible model from the account's current Groq model list.
GROQ_MODEL = os.getenv("GROQ_MODEL")

MONGO_URI = os.getenv("MONGO_URI")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
