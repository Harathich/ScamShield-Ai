from pydantic import BaseModel, Field


class RecruiterResponse(BaseModel):
    agent: str
    risk_score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    threat_level: str
    scam_type: str
    recruitment_legitimacy: str
    red_flags: list[str]
    reason: str
    recommendations: list[str]
