import json

from app.utils.prompt_loader import load_prompt
from app.services.llm.llm_service import LLMService
from app.services.reputation.service import ReputationService


class ReputationAgent:
    """
    Reputation Agent.

    Uses:
    - URLUtils
    - WHOIS
    - VirusTotal

    before asking the LLM to generate
    a structured cybersecurity assessment.
    """

    def __init__(self):

        self.llm = LLMService()

        self.reputation_service = ReputationService()

        self.system_prompt = load_prompt("reputation")

    def analyze(self, url: str) -> dict:

        evidence = self.reputation_service.collect(url)

        user_prompt = f"""
URL:
{evidence['url']}

Domain:
{evidence['domain']}

WHOIS Information:
{json.dumps(evidence['whois'], indent=2)}

VirusTotal Information:
{json.dumps(evidence['virustotal'], indent=2)}

Analyze this evidence and return ONLY valid JSON.
"""

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError:
            raise ValueError(
                "Reputation Agent returned invalid JSON."
            )