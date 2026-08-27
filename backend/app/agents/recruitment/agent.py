import json
import re
from pydantic import ValidationError

from app.services.llm.llm_service import LLMService
from app.utils.prompt_loader import load_prompt


class RecruitmentAgent:

    def __init__(self):
        self.llm = LLMService()
        self.system_prompt = load_prompt("recruitment")

    def analyze(self, text: str) -> dict:
        if not text or not text.strip():
            return {
                "risk_score": 0,
                "risk_level": "LOW",
                "confidence": 1.0,
                "job_information": {},
                "consistency_findings": [],
                "recruitment_red_flags": [],
                "reason": "Empty input provided.",
                "recommendations": []
            }

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=text,
        )

        try:
            parsed_data = self._parse_json(response)
            # Validate against schema to avoid ResponseValidationError later
            from app.models.recruitment_models import RecruitmentResponse
            validated_data = RecruitmentResponse(**parsed_data)
            return validated_data.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            # Fallback for parsing or validation error to prevent 500
            return {
                "risk_score": 50,
                "risk_level": "MEDIUM",
                "confidence": 0.0,
                "job_information": {},
                "consistency_findings": [],
                "recruitment_red_flags": [],
                "reason": "Analysis failed due to malformed response.",
                "recommendations": []
            }

    def _parse_json(self, response: str) -> dict:
        """Robustly parse JSON, handling common LLM formatting issues."""
        text = response.strip()

        # Remove markdown code block markers if present
        if text.startswith("```"):
            # Find the first newline after ```
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline+1:]
            if text.endswith("```"):
                text = text[:-3].strip()

        # Try to find JSON object bounds if there's text before/after
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx+1]

        return json.loads(text)
