import logging
from groq import Groq

from app.config.settings import (
    GROQ_API_KEYS,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)

# Non-chat models that must NEVER be called for chat completions
EXCLUDED_MODEL_SUBSTRINGS = ["prompt-guard", "whisper", "safeguard", "orpheus", "tts", "embedding"]


class LLMService:
    """
    Service responsible for communicating with the Groq API.
    Features:
    1. Multi-key rotation on 429 rate limit errors
    2. Filters out non-chat models (whisper, prompt-guard)
    3. Caches working chat model for fast, reliable inference
    4. Avoids repeated 404s by blacklisting dead models per session
    """

    _cached_model = None      # Last model that worked — try this first
    _dead_models = set()       # Models that 404'd — never try again this session
    _key_index = 0
    _discovered_models = None  # Cache the Groq model list (don't re-fetch every call)

    def __init__(self):
        if not GROQ_API_KEYS:
            raise ValueError("GROQ_API_KEY / GROQ_API_KEYS is not set in environment.")

        self.keys = GROQ_API_KEYS
        self.configured_model = GROQ_MODEL or "openai/gpt-oss-20b"

    def _get_client(self) -> Groq:
        current_key = self.keys[LLMService._key_index % len(self.keys)]
        return Groq(api_key=current_key)

    def _rotate_key(self):
        if len(self.keys) > 1:
            LLMService._key_index = (LLMService._key_index + 1) % len(self.keys)
            logger.info(f"Rotated Groq API key to slot {LLMService._key_index + 1}/{len(self.keys)}")

    def _get_active_models(self, client: Groq) -> list[str]:
        """Fetch list of valid chat models from Groq account. Cached after first call."""

        # Return cached list if we already fetched it
        if LLMService._discovered_models is not None:
            return [m for m in LLMService._discovered_models if m not in LLMService._dead_models]

        try:
            model_list = client.models.list()
            all_ids = [m.id for m in model_list.data if m.active]

            # Filter out non-chat models (audio, prompt-guard, etc.)
            valid_chat_models = []
            for m_id in all_ids:
                if not any(ex in m_id.lower() for ex in EXCLUDED_MODEL_SUBSTRINGS):
                    valid_chat_models.append(m_id)

            # Preferred order — ONLY models known to work on this account
            preferred_order = [
                "openai/gpt-oss-20b",
                "openai/gpt-oss-120b",
                "qwen/qwen3.6-27b",
                "qwen/qwen3.8-27b",
                "groq/compound-mini",
                "groq/compound",
            ]

            sorted_models = []
            for pref in preferred_order:
                if pref in valid_chat_models:
                    sorted_models.append(pref)
            for m_id in valid_chat_models:
                if m_id not in sorted_models:
                    sorted_models.append(m_id)

            LLMService._discovered_models = sorted_models if sorted_models else valid_chat_models
            return [m for m in LLMService._discovered_models if m not in LLMService._dead_models]

        except Exception as e:
            logger.warning(f"Could not dynamically list Groq models: {e}")
            return [
                "openai/gpt-oss-20b",
                "openai/gpt-oss-120b",
                "qwen/qwen3.6-27b",
                "groq/compound-mini",
            ]

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        attempts = 0
        max_attempts = len(self.keys) * 2

        while attempts < max_attempts:
            client = self._get_client()

            candidates = []
            # If we already have a working cached model, try it first (skip all discovery)
            if LLMService._cached_model and LLMService._cached_model not in LLMService._dead_models:
                candidates.append(LLMService._cached_model)

            if self.configured_model and self.configured_model not in candidates and self.configured_model not in LLMService._dead_models:
                candidates.append(self.configured_model)

            active_models = self._get_active_models(client)
            for m in active_models:
                if m not in candidates:
                    candidates.append(m)

            last_exception = None

            for model_name in candidates:
                # Double check: never call prompt-guard or audio models
                if any(ex in model_name.lower() for ex in EXCLUDED_MODEL_SUBSTRINGS):
                    continue
                # Skip known-dead models
                if model_name in LLMService._dead_models:
                    continue

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

                    if "429" in err_msg or "rate_limit" in err_msg or "tokens" in err_msg:
                        logger.warning(f"Rate limit on model {model_name}. Rotating key...")
                        self._rotate_key()
                        break

                    elif any(x in err_msg for x in ["decommissioned", "model_not_found", "not exist", "404", "400", "access"]):
                        logger.warning(f"Groq model '{model_name}' dead/unavailable. Blacklisting for session.")
                        LLMService._dead_models.add(model_name)
                        last_exception = e
                        continue
                    else:
                        raise RuntimeError(f"Groq API Error: {e}")

            attempts += 1

        raise RuntimeError(f"Groq API Error: All keys and models exhausted. Last error: {last_exception}")
