import json

from app.services.llm.llm_service import LLMService
from app.utils.prompt_loader import load_prompt


class ReportGenerator:

    def __init__(self):
        self.llm = LLMService()
        self.system_prompt = load_prompt("report_generator")

    def generate(self, analysis_data: dict) -> dict:
        """
        Generate a user-friendly report from the combined analysis data.

        Args:
            analysis_data: Dict containing all agent results and risk manager output.

        Returns:
            Dict with the structured report.
        """
        user_prompt = json.dumps(analysis_data, indent=2)

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
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
                raise ValueError("Report Generator returned invalid JSON.")
