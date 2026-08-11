from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DomainAnalyzeRequest(BaseModel):
    url: str


class DomainAnalyzeResponse(BaseModel):
    agent: str = "domain"
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    domain: str
    domain_age: str
    ssl_status: str
    whois: Dict[str, Any]
    brand_impersonation: bool
    technical_red_flags: List[str]
    recommendation: str
    explanation: str
    reputation: Optional[Dict[str, Any]] = None
