from pydantic import BaseModel, Field


class IdentityResponse(BaseModel):
    agent: str
    risk_score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    threat_level: str
    claimed_identity: str
    identity_type: str
    verification_status: str
    red_flags: list[str]
    reason: str
    recommendations: list[str]
