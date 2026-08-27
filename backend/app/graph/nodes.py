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
from app.agents.recruitment.agent import RecruitmentAgent
from app.agents.risk_manager.agent import RiskManager
from app.agents.report_generator.agent import ReportGenerator


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


def recruitment_node(state: ScamShieldState) -> dict:
    """
    Run the Recruitment Agent on the input text.

    This agent analyzes job/recruitment scam indicators and job detail consistency.
    It runs on all inputs — the agent itself determines
    whether the content is recruitment-related.
    """
    try:
        agent = RecruitmentAgent()
        result = agent.analyze(state["input_text"])
        return {"recruitment_result": result}
    except Exception as e:
        return {"recruitment_result": {"agent": "recruitment", "error": str(e)}}


def risk_manager_node(state: ScamShieldState) -> dict:
    """
    Run the Risk Manager to aggregate all agent results.

    Collects results from all agents, computes weighted overall
    risk score, and determines the overall threat level.
    """
    agent_results = {
        "threat": state.get("threat_result"),
        "language": state.get("language_result"),
        "identity": state.get("identity_result"),
        "domain": state.get("domain_result"),
        "recruitment": state.get("recruitment_result"),
    }

    try:
        risk_manager = RiskManager()
        result = risk_manager.evaluate(agent_results)
        return {
            "risk_manager_result": result,
            "overall_risk_score": result["overall_risk_score"],
            "overall_threat_level": result["overall_threat_level"],
            "agent_summary": result["agent_scores"],
        }
    except Exception as e:
        return {
            "risk_manager_result": {"error": str(e)},
            "overall_risk_score": 0,
            "overall_threat_level": "LOW",
            "agent_summary": {},
        }


def report_node(state: ScamShieldState) -> dict:
    """
    Run the Report Generator to produce a user-friendly report.

    Feeds all agent results + Risk Manager output to the LLM
    to generate a plain-language security report.
    """
    analysis_data = {
        "input_text": state["input_text"],
        "threat_result": state.get("threat_result"),
        "language_result": state.get("language_result"),
        "identity_result": state.get("identity_result"),
        "domain_result": state.get("domain_result"),
        "recruitment_result": state.get("recruitment_result"),
        "risk_manager_result": state.get("risk_manager_result"),
    }

    try:
        generator = ReportGenerator()
        report = generator.generate(analysis_data)
        return {"report": report}
    except Exception as e:
        return {"report": {"agent": "report_generator", "error": str(e)}}
