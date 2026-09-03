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

        # 1b. If SSRF protection blocked this URL, return deterministic result (no LLM call)
        if technical_evidence.get('ssrf_blocked'):
            return {
                "agent": "domain",
                "risk_score": 0,
                "risk_level": "LOW",
                "domain": technical_evidence.get('domain', url),
                "domain_age": "Unknown",
                "ssl_status": "Unknown",
                "whois": {},
                "brand_impersonation": False,
                "ssrf_blocked": True,
                "technical_red_flags": ["Target resolves to a private or internal network address"],
                "explanation": technical_evidence.get('error', 'SSRF blocked: private/internal address.'),
                "recommendation": "Do not access internal/private network URLs from this tool."
            }

        # 2. Convert evidence to JSON string for the LLM prompt
        from datetime import datetime
        current_time_context = f"\n\nCURRENT SYSTEM TIME: {datetime.now().isoformat()}\nUse this to calculate relative dates."
        user_prompt = json.dumps(technical_evidence, indent=2) + current_time_context

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
