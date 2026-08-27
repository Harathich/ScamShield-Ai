"""
LangGraph node functions for the ScamShield multi-agent pipeline.

Each node takes the shared ScamShieldState, runs one agent,
and returns a dict with updated state fields.
If an agent fails, the error is captured in the result
rather than crashing the pipeline.
"""

import re

from app.graph.state import ScamShieldState
from app.agents.threat.agent import ThreatAgent
from app.agents.language.agent import LanguageAgent
from app.agents.identity.agent import IdentityAgent
from app.agents.domain.agent import DomainAgent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_url_from_text(text: str):
    """Extract the first URL found in a block of text. Returns None if none found."""
    pattern = r'https?://[^\s<>\"\'\)\]}]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


# ---------------------------------------------------------------------------
# Agent Nodes
# ---------------------------------------------------------------------------

def threat_node(state: ScamShieldState) -> dict:
    """Run the Threat Agent on the input text."""
    try:
        agent = ThreatAgent()
        result = agent.analyze(state["input_text"])
        return {"threat_result": result}
    except Exception as e:
        return {"threat_result": {"agent": "threat", "error": str(e)}}


def language_node(state: ScamShieldState) -> dict:
    """Run the Language Agent on the input text."""
    try:
        agent = LanguageAgent()
        result = agent.analyze(state["input_text"])
        return {"language_result": result}
    except Exception as e:
        return {"language_result": {"agent": "language", "error": str(e)}}


def identity_node(state: ScamShieldState) -> dict:
    """Run the Identity Agent on the input text."""
    try:
        agent = IdentityAgent()
        result = agent.analyze(state["input_text"])
        return {"identity_result": result}
    except Exception as e:
        return {"identity_result": {"agent": "identity", "error": str(e)}}


def domain_node(state: ScamShieldState) -> dict:
    """
    Run the Domain Agent if a URL is available.

    URL sources (in priority order):
    1. Explicitly provided `input_url`
    2. Auto-extracted from `input_text`

    If no URL is found, the domain agent is skipped.
    """
    url = state.get("input_url")

    if not url:
        url = _extract_url_from_text(state["input_text"])

    if not url:
        return {"domain_result": {
            "agent": "domain",
            "skipped": True,
            "reason": "No URL found in input."
        }}

    try:
        agent = DomainAgent()
        result = agent.analyze(url)
        return {"domain_result": result}
    except Exception as e:
        return {"domain_result": {"agent": "domain", "error": str(e)}}


def aggregate_node(state: ScamShieldState) -> dict:
    """
    Combine individual agent results into an overall risk assessment.

    Scoring logic (placeholder until Risk Manager is built):
    - Collects risk_score from each agent that returned one
    - Overall score = maximum individual score (worst-case signal)
    - Overall threat level derived from the overall score
    """
    scores = []

    for key in ["threat_result", "language_result", "identity_result", "domain_result"]:
        result = state.get(key)
        if result and isinstance(result, dict) and "risk_score" in result:
            scores.append(result["risk_score"])

    if scores:
        overall_score = max(scores)
    else:
        overall_score = 0

    if overall_score >= 76:
        level = "CRITICAL"
    elif overall_score >= 51:
        level = "HIGH"
    elif overall_score >= 26:
        level = "MEDIUM"
    else:
        level = "LOW"

    summary = {}
    for key in ["threat_result", "language_result", "identity_result", "domain_result"]:
        result = state.get(key)
        if result and isinstance(result, dict):
            agent_name = key.replace("_result", "")
            summary[agent_name] = {
                "risk_score": result.get("risk_score", None),
                "threat_level": result.get("threat_level", result.get("risk_level", None)),
                "skipped": result.get("skipped", False),
                "error": result.get("error", None),
            }

    return {
        "overall_risk_score": overall_score,
        "overall_threat_level": level,
        "agent_summary": summary,
    }
