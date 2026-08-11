from pydantic import BaseModel, Field


class LanguageResponse(BaseModel):
    agent: str
    risk_score: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    threat_level: str
    summary: str
    manipulation_techniques: list[str]
    reason: str
    recommendations: list[str]