from pydantic import BaseModel, Field


class ReputationResponse(BaseModel):
    """
    Response model returned by Reputation Agent.
    """

    agent: str

    risk_score: int = Field(
        ge=0,
        le=100
    )

    threat_level: str

    reputation: str

    malicious_engines: int

    domain: str

    registered: bool

    registrar: str | None

    creation_date: str | None

    domain_age_days: int | None

    findings: list[str]

    reason: str

    recommendations: list[str]
    