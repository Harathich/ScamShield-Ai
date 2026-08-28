import json
from app.utils.prompt_loader import load_prompt

from app.services.llm.llm_service import LLMService


class ThreatAgent:

    def __init__(self):
        self.llm = LLMService()

        self.system_prompt = load_prompt("threat")

    def analyze(self, text: str) -> dict:

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=text,
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception:
                raise ValueError("Threat Agent returned invalid JSON.")