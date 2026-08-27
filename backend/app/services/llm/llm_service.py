import logging
from groq import Groq

from app.config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)

# Only these general-purpose chat models are valid for the agent prompts below.
# Prompt Guard models are intentionally excluded: they are classifiers that
# require a single user message and cannot process system + user chat prompts.
CHAT_MODEL_IDS = (
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-16e-instruct",
)


class LLMService:
    """
    Service responsible for communicating with the Groq API.
    Dynamically resolves and verifies active models to ensure seamless availability.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.configured_model = GROQ_MODEL

    def _get_active_models(self) -> list[str]:
        """Return supported chat models that this Groq account exposes."""
        try:
            model_list = self.client.models.list()
            available_ids = {
                model.id for model in model_list.data
                if getattr(model, "active", True)
            }
            return [model_id for model_id in CHAT_MODEL_IDS if model_id in available_ids]

        except Exception as e:
            logger.warning(f"Could not dynamically list Groq models: {e}")
            return []

    def generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        active_models = self._get_active_models()
        candidates = list(active_models)

        if self.configured_model:
            if self.configured_model in active_models:
                candidates.remove(self.configured_model)
                candidates.insert(0, self.configured_model)
            else:
                logger.warning(
                    "Configured GROQ_MODEL '%s' is unavailable or incompatible; "
                    "using a discovered chat model instead.",
                    self.configured_model,
                )

        if not candidates:
            raise RuntimeError(
                "Groq API Error: no compatible chat model is available for this API key. "
                "Use a key with access to a supported Groq chat model."
            )

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
                logger.info("Groq request succeeded with model '%s'.", model_name)
                return response.choices[0].message.content

            except Exception as e:
                err_msg = str(e).lower()
                # Only retry errors caused by an unavailable model. A generic
                # 400 is a malformed request and must be reported directly.
                if any(x in err_msg for x in ["decommissioned", "model_not_found", "not exist", "404"]):
                    logger.warning(f"Groq model '{model_name}' skipped ({e}). Trying next available model...")
                    last_exception = e
                    continue
                else:
                    # Rate limit or critical auth failures
                    raise RuntimeError(f"Groq API Error: {e}")

        raise RuntimeError(f"Groq API Error: All attempted models failed. Last error: {last_exception}")
