import json
from pydantic import ValidationError

from app.services.llm.llm_service import LLMService
from app.utils.prompt_loader import load_prompt
from app.models.identity_response import IdentityResponse, IdentityEntities


class IdentityAgent:

    def __init__(self):
        self.llm = LLMService()
        self.system_prompt = load_prompt("identity")

    def analyze(self, text: str) -> dict:
        if not text or not text.strip():
            return IdentityResponse(
                agent="identity",
                risk_score=0,
                confidence=1.0,
                threat_level="LOW",
                verification_status="INCONCLUSIVE",
                identity_entities=IdentityEntities(),
                mismatch_findings=[],
                identity_red_flags=[],
                reason="Empty input provided.",
                recommendations=[]
            ).model_dump()

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=text,
        )

        try:
            parsed_data = self._parse_json(response)
            validated_data = IdentityResponse(**parsed_data)
            return validated_data.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            # Safe fallback if response is malformed to avoid 500 errors
            return IdentityResponse(
                agent="identity",
                risk_score=30,
                confidence=0.0,
                threat_level="MEDIUM",
                verification_status="INCONCLUSIVE",
                identity_entities=IdentityEntities(),
                mismatch_findings=[],
                identity_red_flags=["Malformed agent response"],
                reason=f"Identity analysis completed with parsing warning: {str(e)}",
                recommendations=["Verify sender identity directly through official channels."]
            ).model_dump()

    def _parse_json(self, response: str) -> dict:
        """Robustly parse JSON, handling common LLM formatting issues."""
        text = response.strip()

        # Remove markdown code block markers if present
        if text.startswith("```"):
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline + 1:]
            if text.endswith("```"):
                text = text[:-3].strip()

        # Extract JSON object bounds if there's text before/after
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1:
            text = text[start_idx:end_idx + 1]

        return json.loads(text)
