import logging
from groq import Groq

from app.config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service responsible for communicating with the Groq API.
    Dynamically resolves and verifies active models to ensure seamless availability.
    """

    _cached_model = None

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.configured_model = GROQ_MODEL

    def _get_active_models(self) -> list[str]:
        """Fetch list of active model IDs directly from the Groq account."""
        try:
            model_list = self.client.models.list()
            # Prioritize Llama 3.3, Llama 3.2, Llama 3.1, Mixtral, Gemma
            all_ids = [m.id for m in model_list.data if m.active]
            
            # Sort with preferred models first
            preferred_order = [
                "llama-3.3-70b-versatile",
                "llama-3.3-70b-specdec",
                "llama-3.2-11b-vision-preview",
                "llama-3.2-3b-preview",
                "llama-3.1-8b-instant",
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
                "llama-3.3-70b-versatile",
                "llama-3.2-3b-preview",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ]

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        # Build list of candidates to try
        candidates = []
        if self.configured_model:
            candidates.append(self.configured_model)
        
        active_models = self._get_active_models()
        for m in active_models:
            if m not in candidates:
                candidates.append(m)

        last_exception = None

        for model_name in candidates:
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
                # Cache the successful model
                LLMService._cached_model = model_name
                return response.choices[0].message.content

            except Exception as e:
                err_msg = str(e).lower()
                # Catch decommissioned, not found, or inaccessible model errors and try next
                if any(x in err_msg for x in ["decommissioned", "model_not_found", "not exist", "404", "400", "access"]):
                    logger.warning(f"Groq model '{model_name}' skipped ({e}). Trying next available model...")
                    last_exception = e
                    continue
                else:
                    # Rate limit or critical auth failures
                    raise RuntimeError(f"Groq API Error: {e}")

        raise RuntimeError(f"Groq API Error: All attempted models failed. Last error: {last_exception}")