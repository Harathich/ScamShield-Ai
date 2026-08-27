from pydantic import BaseModel, Field
from typing import Optional


class FullAnalysisRequest(BaseModel):
    """Request model for the full multi-agent analysis pipeline."""
    text: str
    url: Optional[str] = None


class AgentSummary(BaseModel):
    """Summary of a single agent's result within the orchestrated response."""
    risk_score: Optional[int] = None
    threat_level: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None


class FullAnalysisResponse(BaseModel):
    """Response model for the full multi-agent analysis pipeline."""
    overall_risk_score: int = Field(ge=0, le=100)
    overall_threat_level: str
    contributing_factors: list[str] = []
    confidence: int = Field(ge=0, le=100, default=0)
    agent_summary: dict[str, AgentSummary]
    report: Optional[dict] = None
    threat_result: Optional[dict] = None
    language_result: Optional[dict] = None
    identity_result: Optional[dict] = None
    domain_result: Optional[dict] = None
    recruiter_result: Optional[dict] = None
