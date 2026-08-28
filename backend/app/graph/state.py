"""
Shared state definition for the ScamShield multi-agent orchestration graph.

This TypedDict flows through every node in the LangGraph workflow.
Each agent node reads `input_text` (and optionally `input_url`),
runs its analysis, and writes its result into the corresponding field.
"""

from typing import Optional
from typing_extensions import TypedDict


class ScamShieldState(TypedDict):
    """State that flows through the ScamShield analysis pipeline."""

    # --- Raw Inputs ---
    input_text: str
    input_url: Optional[str]

    # --- Preprocessed / Normalized Content ---
    normalized_content: Optional[dict]

    # --- Agent Results ---
    threat_result: Optional[dict]
    language_result: Optional[dict]
    identity_result: Optional[dict]
    domain_result: Optional[dict]
    recruitment_result: Optional[dict]

    # --- Risk Manager Output ---
    risk_manager_result: Optional[dict]

    # --- Report Generator Output ---
    report: Optional[dict]

    # --- Aggregated Output (from Risk Manager) ---
    overall_risk_score: Optional[int]
    overall_threat_level: Optional[str]
    agent_summary: Optional[dict]
