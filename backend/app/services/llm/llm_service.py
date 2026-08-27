import logging
from groq import Groq

from app.config.settings import (
    GROQ_API_KEYS,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service responsible for communicating with the Groq API.
    Features:
    1. Multi-key rotation on 429 rate limit errors
    2. Dynamic model discovery prioritizing high-limit lightweight models (llama-3.1-8b-instant)
    3. Resilient fallback across active Groq models
    """

    _cached_model = None
    _key_index = 0

    def __init__(self):
        if not GROQ_API_KEYS:
            raise ValueError("GROQ_API_KEY / GROQ_API_KEYS is not set in environment.")

        self.keys = GROQ_API_KEYS
        self.configured_model = GROQ_MODEL or "llama-3.1-8b-instant"

    def _get_client(self) -> Groq:
        current_key = self.keys[LLMService._key_index % len(self.keys)]
        return Groq(api_key=current_key)

    def _rotate_key(self):
        if len(self.keys) > 1:
            LLMService._key_index = (LLMService._key_index + 1) % len(self.keys)
            logger.info(f"Rotated Groq API key to slot {LLMService._key_index + 1}/{len(self.keys)}")

    def _get_active_models(self, client: Groq) -> list[str]:
        """Fetch list of active model IDs from Groq, prioritizing high-quota fast models."""
        try:
            model_list = client.models.list()
            all_ids = [m.id for m in model_list.data if m.active]

            preferred_order = [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "llama-3.3-70b-specdec",
                "llama-3.2-11b-vision-preview",
                "llama-3.2-3b-preview",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ]

            sorted_models = []
            for pref in preferred_order:
                if pref in all_ids:
                    sorted_models.append(pref)
            for m_id in all_ids:
                if m_id not in sorted_models and ("llama" in m_id or "mixtral" in m_id or "gemma" in m_id):
                    sorted_models.append(m_id)

            return sorted_models if sorted_models else all_ids

        except Exception as e:
            logger.warning(f"Could not dynamically list Groq models: {e}")
            return [
                "llama-3.1-8b-instant",
                "llama-3.3-70b-versatile",
                "llama-3.2-3b-preview",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ]

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        # Loop across available keys in case of rate limits
        attempts = 0
        max_attempts = len(self.keys) * 2

        while attempts < max_attempts:
            client = self._get_client()

            # Build list of model candidates to try
            candidates = []
            if self.configured_model:
                candidates.append(self.configured_model)

            active_models = self._get_active_models(client)
            for m in active_models:
                if m not in candidates:
                    candidates.append(m)

            last_exception = None

            for model_name in candidates:
                try:
                    response = client.chat.completions.create(
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
                    LLMService._cached_model = model_name
                    return response.choices[0].message.content

                except Exception as e:
                    err_msg = str(e).lower()

                    # Handle Rate Limit (429) -> Rotate to next key if available
                    if "429" in err_msg or "rate_limit" in err_msg or "tokens" in err_msg:
                        logger.warning(f"Rate limit hit on model {model_name}. Rotating key...")
                        self._rotate_key()
                        break  # Break out to outer loop to retry with new client key

                    # Handle decommissioned/unavailable model -> Try next model
                    elif any(x in err_msg for x in ["decommissioned", "model_not_found", "not exist", "404", "400", "access"]):
                        logger.warning(f"Groq model '{model_name}' skipped ({e}). Trying next model...")
                        last_exception = e
                        continue
                    else:
                        raise RuntimeError(f"Groq API Error: {e}")

            attempts += 1

        raise RuntimeError(f"Groq API Error: All keys and models exhausted. Last error: {last_exception}")
