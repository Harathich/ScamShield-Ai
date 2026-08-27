from typing import List, Optional
from pydantic import BaseModel, Field


class IdentityEntities(BaseModel):
    claimed_name: Optional[str] = None
    claimed_organization: Optional[str] = None
    claimed_role_or_title: Optional[str] = None
    sender_email: Optional[str] = None
    sender_domain: Optional[str] = None
    domain_type: Optional[str] = Field(
        default=None,
        description="corporate | public_webmail | lookalike_spoof | unknown"
    )
    contact_identifiers: List[str] = Field(default_factory=list)


class IdentityMismatch(BaseModel):
    category: str = Field(description="e.g. domain_vs_brand, public_webmail_for_corporate, signature_contradiction")
    finding: str
    evidence: str


class IdentityResponse(BaseModel):
    agent: str = "identity"
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    threat_level: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL")
    verification_status: str = Field(description="VERIFIED | SUSPICIOUS | IMPERSONATION | INCONCLUSIVE")
    identity_entities: IdentityEntities = Field(default_factory=IdentityEntities)
    mismatch_findings: List[IdentityMismatch] = Field(default_factory=list)
    identity_red_flags: List[str] = Field(default_factory=list)
    reason: str
    recommendations: List[str] = Field(default_factory=list)
