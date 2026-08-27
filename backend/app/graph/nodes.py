"""
LangGraph node functions for the ScamShield multi-agent pipeline.

Each node takes the shared ScamShieldState, runs one agent or transformation,
and returns a dict with updated state fields.
"""

from app.graph.state import ScamShieldState
from app.utils.preprocessor import ContentPreprocessor
from app.agents.threat.agent import ThreatAgent
from app.agents.language.agent import LanguageAgent
from app.agents.identity.agent import IdentityAgent
from app.agents.domain.agent import DomainAgent
from app.agents.recruitment.agent import RecruitmentAgent
from app.agents.risk_manager.agent import RiskManager
from app.agents.report_generator.agent import ReportGenerator


# ---------------------------------------------------------------------------
# Preprocessing Node (Input Normalizer)
# ---------------------------------------------------------------------------

def preprocess_node(state: ScamShieldState) -> dict:
    """
    Normalizes messy/unstructured input, removes noise, and extracts entities.
    """
    try:
        norm = ContentPreprocessor.process(
            raw_input=state.get("input_text", ""),
            explicit_url=state.get("input_url")
        )
        return {"normalized_content": norm.model_dump()}
    except Exception as e:
        # Fallback if preprocessing encounters an unexpected issue
        return {"normalized_content": {
            "clean_text": state.get("input_text", ""),
            "raw_text": state.get("input_text", ""),
            "extracted_urls": [state["input_url"]] if state.get("input_url") else [],
            "extracted_emails": [],
            "extracted_phones": [],
            "detected_format": "plain_text"
        }}


# ---------------------------------------------------------------------------
# Agent Nodes
# ---------------------------------------------------------------------------

def threat_node(state: ScamShieldState) -> dict:
    """Run the Threat Agent on the clean normalized text."""
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    try:
        agent = ThreatAgent()
        result = agent.analyze(text)
        return {"threat_result": result}
    except Exception as e:
        return {"threat_result": {"agent": "threat", "error": str(e)}}


def language_node(state: ScamShieldState) -> dict:
    """Run the Language Agent on the clean normalized text."""
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    try:
        agent = LanguageAgent()
        result = agent.analyze(text)
        return {"language_result": result}
    except Exception as e:
        return {"language_result": {"agent": "language", "error": str(e)}}


def identity_node(state: ScamShieldState) -> dict:
    """Run the Identity Agent on the clean normalized text."""
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    try:
        agent = IdentityAgent()
        result = agent.analyze(text)
        return {"identity_result": result}
    except Exception as e:
        return {"identity_result": {"agent": "identity", "error": str(e)}}


def domain_node(state: ScamShieldState) -> dict:
    """
    Run the Domain Agent if a URL is available (from explicit input or extracted by preprocessor).
    """
    norm = state.get("normalized_content", {})
    extracted_urls = norm.get("extracted_urls", [])

    url = state.get("input_url")
    if not url and extracted_urls:
        url = extracted_urls[0]

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
    Run the Recruitment Agent on the clean normalized text.
    """
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    try:
        agent = RecruitmentAgent()
        result = agent.analyze(text)
        return {"recruitment_result": result}
    except Exception as e:
        return {"recruitment_result": {"agent": "recruitment", "error": str(e)}}


def risk_manager_node(state: ScamShieldState) -> dict:
    """
    Run the Risk Manager to aggregate all agent results.
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
    """
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")

    analysis_data = {
        "input_text": text,
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
