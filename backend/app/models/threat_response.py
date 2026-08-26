from pydantic import BaseModel,Field


class ThreatResponse(BaseModel):
    agent: str
    risk_score: int = Field(ge = 0, le=100)
    threat_level: str
    scam_type: str
    red_flags: list[str]
    reason: str
    recommendations: list[str]
    