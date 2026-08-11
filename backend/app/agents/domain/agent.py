import json
from app.utils.prompt_loader import load_prompt
from app.services.llm.llm_service import LLMService
from app.agents.domain.analyzer import DomainAnalyzer


class DomainAgent:
    def __init__(self):
        self.llm = LLMService()
        self.analyzer = DomainAnalyzer()
        # Ensure we load the correct prompt. Assuming prompt_loader reads from prompts/domain/system_prompt.md
        self.system_prompt = load_prompt("domain")

    def analyze(self, url: str) -> dict:
        # 1. Perform technical analysis
        technical_evidence = self.analyzer.analyze(url)
        
        # 2. Convert evidence to JSON string for the LLM prompt
        user_prompt = json.dumps(technical_evidence, indent=2)
        
        # 3. Generate response from LLM
        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )

        # 4. Parse JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if LLM fails to return strict JSON
            # Sometimes LLMs wrap JSON in markdown blocks
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
                raise ValueError("Domain Agent returned invalid JSON.")
