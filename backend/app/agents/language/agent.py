import json

from app.services.llm.llm_service import LLMService
from app.utils.prompt_loader import load_prompt


class LanguageAgent:

    def __init__(self):
        self.llm = LLMService()
        self.system_prompt = load_prompt("language")

    def analyze(self, text: str) -> dict:

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=text,
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError:
            raise ValueError("Language Agent returned invalid JSON.")