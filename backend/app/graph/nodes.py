"""
LangGraph node functions for the ScamShield multi-agent pipeline.

Optimized Hybrid Architecture:
1. Deterministic preprocessing & regex entity extraction (0 tokens)
2. Smart Conditional Gating:
   - Domain Agent: Runs only when URL is present (0 tokens if no URL)
   - Recruitment Agent: Runs only when job/recruitment keywords exist (0 tokens for general text)
   - Identity Agent: Fast-paths inconclusive status when no identity indicators exist (0 tokens)
   - Language Agent: Fast-paths simple neutral messages when no manipulation cues exist (0 tokens)
3. Deterministic Risk Manager (0 tokens)
4. Deterministic Report Generator (0 tokens)
"""

import re
from app.graph.state import ScamShieldState
from app.utils.preprocessor import ContentPreprocessor
from app.agents.threat.agent import ThreatAgent
from app.agents.language.agent import LanguageAgent
from app.agents.identity.agent import IdentityAgent
from app.agents.domain.agent import DomainAgent
from app.agents.recruitment.agent import RecruitmentAgent
from app.agents.risk_manager.agent import RiskManager
from app.agents.report_generator.agent import ReportGenerator


# Keywords for conditional recruitment agent execution
RECRUITMENT_KEYWORDS = {
    "job", "jobs", "salary", "hiring", "hired", "recruit", "recruiting", "recruiter",
    "interview", "resume", "cv", "intern", "internship", "interns", "work from home",
    "wfh", "data entry", "stipend", "vacancy", "vacancies", "career", "careers",
    "applicant", "applicants", "employment", "candidate", "candidates", "joining",
    "hr coordinator", "hr manager", "hr team", "remuneration", "per month", "per year",
    "lpa", "$/hr", "$/year", "annual package"
}

# Manipulation signals for fast-path check
MANIPULATION_KEYWORDS = {
    "urgent", "urgently", "hurry", "expire", "expires", "suspended", "blocked",
    "warning", "alert", "immediate", "immediately", "bonus", "prize", "won",
    "winner", "lottery", "reward", "lucky draw", "trojan", "virus", "infected",
    "deadline", "limited time", "act now", "last chance", "free cash"
}


# ---------------------------------------------------------------------------
# Preprocessing Node (Input Normalizer)
# ---------------------------------------------------------------------------

def preprocess_node(state: ScamShieldState) -> dict:
    """Normalizes messy/unstructured input, removes noise, and extracts entities."""
    try:
        norm = ContentPreprocessor.process(
            raw_input=state.get("input_text", ""),
            explicit_url=state.get("input_url")
        )
        return {"normalized_content": norm.model_dump()}
    except Exception:
        return {"normalized_content": {
            "clean_text": state.get("input_text", ""),
            "raw_text": state.get("input_text", ""),
            "extracted_urls": [state["input_url"]] if state.get("input_url") else [],
            "extracted_emails": [],
            "extracted_phones": [],
            "detected_format": "plain_text"
        }}


# ---------------------------------------------------------------------------
# Agent Nodes with Smart Gating
# ---------------------------------------------------------------------------

def threat_node(state: ScamShieldState) -> dict:
    """Run the Threat Agent on the clean normalized text."""
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    
    # Fast path for very short empty text
    if not text.strip():
        return {"threat_result": {
            "agent": "threat",
            "risk_score": 0,
            "threat_level": "LOW",
            "scam_type": "None",
            "red_flags": [],
            "reason": "Empty input provided.",
            "recommendations": []
        }}

    try:
        agent = ThreatAgent()
        result = agent.analyze(text)
        return {"threat_result": result}
    except Exception as e:
        return {"threat_result": {"agent": "threat", "error": str(e)}}


def language_node(state: ScamShieldState) -> dict:
    """
    Run Language Agent. Fast-paths simple neutral messages without LLM calls.
    """
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    words = set(re.findall(r'\b\w+\b', text.lower()))

    # Fast-path: If text is short and has zero manipulation keywords, skip LLM call
    if len(words) < 20 and not words.intersection(MANIPULATION_KEYWORDS):
        return {"language_result": {
            "agent": "language",
            "risk_score": 0,
            "confidence": 95,
            "threat_level": "LOW",
            "summary": "The message is neutral and informational with no psychological pressure tactics.",
            "manipulation_techniques": [],
            "reason": "No urgency, fear, reward, or pressure signals detected.",
            "recommendations": []
        }}

    try:
        agent = LanguageAgent()
        result = agent.analyze(text)
        return {"language_result": result}
    except Exception as e:
        return {"language_result": {"agent": "language", "error": str(e)}}


def identity_node(state: ScamShieldState) -> dict:
    """
    Run Identity Agent. Fast-paths inconclusive status when no sender indicators exist.
    """
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    emails = norm.get("extracted_emails", [])
    phones = norm.get("extracted_phones", [])

    # Fast-path: If message has no emails, phones, and no identity claim headers, skip LLM
    has_header = bool(re.search(r'^(?:From:|Reply-To:|Sender:)', text, re.IGNORECASE | re.MULTILINE))
    if not emails and not phones and not has_header and len(text.split()) < 25:
        return {"identity_result": {
            "agent": "identity",
            "risk_score": 0,
            "confidence": 0.5,
            "threat_level": "LOW",
            "verification_status": "INCONCLUSIVE",
            "identity_entities": {
                "claimed_name": None,
                "claimed_organization": None,
                "claimed_role_or_title": None,
                "sender_email": None,
                "sender_domain": None,
                "domain_type": None,
                "contact_identifiers": []
            },
            "mismatch_findings": [],
            "identity_red_flags": [],
            "reason": "The message contains no sender headers or identity claims; verification is inconclusive.",
            "recommendations": []
        }}

    try:
        agent = IdentityAgent()
        result = agent.analyze(text)
        return {"identity_result": result}
    except Exception as e:
        return {"identity_result": {"agent": "identity", "error": str(e)}}


def domain_node(state: ScamShieldState) -> dict:
    """Run Domain Agent if a URL is present. Skips (0 tokens) if no URL."""
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
    Run Recruitment Agent with smart gating.
    Only queries the LLM if the text actually contains recruitment-related terms.
    Saves 100% of tokens on ordinary transactional, casual, or banking messages!
    """
    norm = state.get("normalized_content", {})
    text = norm.get("clean_text") or state.get("input_text", "")
    words = set(re.findall(r'\b\w+\b', text.lower()))

    # Check if any recruitment keywords exist in the text
    has_recruitment_keywords = bool(words.intersection(RECRUITMENT_KEYWORDS))

    if not has_recruitment_keywords:
        return {"recruitment_result": {
            "risk_score": 0,
            "risk_level": "LOW",
            "confidence": 1.0,
            "job_information": {
                "job_title": None, "company_claim": None, "department": None,
                "role": None, "job_type": None, "work_arrangement": None,
                "experience": None, "education": None, "skills": [],
                "responsibilities": [], "location": None, "employment_type": None,
                "compensation": None, "benefits": [], "application_method": None,
                "contact_method": None, "interview_process": None, "recruiter_instructions": None
            },
            "consistency_findings": [],
            "recruitment_red_flags": [],
            "reason": "No employment or recruitment context detected in this message.",
            "recommendations": []
        }}

    try:
        agent = RecruitmentAgent()
        result = agent.analyze(text)
        return {"recruitment_result": result}
    except Exception as e:
        return {"recruitment_result": {"agent": "recruitment", "error": str(e)}}


def risk_manager_node(state: ScamShieldState) -> dict:
    """Run Risk Manager (Deterministic Math, 0 tokens)."""
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
    """Run Report Generator (Deterministic Synthesis, 0 tokens)."""
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
