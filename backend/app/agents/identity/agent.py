import json
from pydantic import ValidationError

from app.services.llm.llm_service import LLMService
from app.utils.prompt_loader import load_prompt
from app.models.identity_response import IdentityResponse, IdentityEntities

import re
from urllib.parse import urlparse

class IdentityAgent:

    def __init__(self):
        self.llm = LLMService()
        self.system_prompt = load_prompt("identity")
        self.known_brands = {
            "microsoft": ["microsoft.com", "live.com", "outlook.com"],
            "apple": ["apple.com", "icloud.com"],
            "google": ["google.com", "gmail.com"],
            "netflix": ["netflix.com"],
            "paypal": ["paypal.com"],
            "sbi": ["sbi.co.in", "onlinesbi.com", "onlinesbi.sbi"],
            "amazon": ["amazon.com"],
            "github": ["github.com"],
            "facebook": ["facebook.com", "meta.com"],
            "instagram": ["instagram.com"],
            "twitter": ["twitter.com", "x.com"],
            "whatsapp": ["whatsapp.com"],
            "linkedin": ["linkedin.com"],
            "stripe": ["stripe.com"]
        }

    def _get_domain(self, url: str) -> str:
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            parsed = urlparse(url)
            domain = parsed.netloc.split(':')[0]
            return domain.lower()
        except Exception:
            return ""

    def _run_deterministic_checks(self, text: str) -> list:
        text_lower = text.lower()
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        findings = []

        mentioned_brands = []
        for brand, legit_domains in self.known_brands.items():
            if re.search(r'\b' + brand + r'\b', text_lower):
                mentioned_brands.append((brand, legit_domains))

        if mentioned_brands and urls:
            for url in urls:
                domain = self._get_domain(url)
                for brand, legit_domains in mentioned_brands:
                    is_legit = False
                    for ld in legit_domains:
                        if domain == ld or domain.endswith("." + ld):
                            is_legit = True
                            break
                    if not is_legit:
                        findings.append(f"CRITICAL MISMATCH: Message mentions '{brand.capitalize()}' but contains URL pointing to unrelated domain '{domain}'. This is a strong indicator of brand impersonation.")
                    else:
                        findings.append(f"VERIFIED BRAND: Message mentions '{brand.capitalize()}' and contains official matching domain '{domain}'.")
        return findings

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

        deterministic_findings = self._run_deterministic_checks(text)

        user_prompt = text
        if deterministic_findings:
            user_prompt += "\n\n--- SYSTEM DETERMINISTIC FINDINGS ---\n"
            for f in deterministic_findings:
                user_prompt += f"- {f}\n"
            user_prompt += "\nINSTRUCTION: Strongly weigh these deterministic findings when assigning the verification_status and risk_score. A CRITICAL MISMATCH should result in IMPERSONATION and HIGH/CRITICAL risk."

        response = self.llm.generate_content(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
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
