from groq import Groq
import logging

from app.config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)

# Fallback models in priority order if the configured model is unavailable
FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]


class LLMService:
    """
    Service responsible for communicating with the Groq API.
    Handles model fallbacks if a requested model ID is retired or restricted.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.primary_model = GROQ_MODEL or "llama-3.1-8b-instant"

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        models_to_try = [self.primary_model] + [m for m in FALLBACK_MODELS if m != self.primary_model]
        last_exception = None

        for model_name in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content

            except Exception as e:
                err_msg = str(e)
                # If error is model_not_found / 404, try next model in fallback list
                if "model_not_found" in err_msg or "404" in err_msg:
                    logger.warning(f"Groq model '{model_name}' not available. Trying fallback...")
                    last_exception = e
                    continue
                else:
                    # Other errors (e.g. rate limit, auth) should be raised immediately
                    raise RuntimeError(f"Groq API Error: {e}")

        raise RuntimeError(f"Groq API Error: {last_exception}")