import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator


class DomainAnalyzeRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_url(cls, values: Any) -> Any:
        if isinstance(values, str):
            return {"url": values}
        if isinstance(values, dict):
            raw_url = values.get("url") or values.get("link") or values.get("website") or values.get("domain")
            if not raw_url and values.get("text"):
                # Extract URL from text if present
                match = re.search(r'https?://[^\s]+', str(values.get("text")))
                if match:
                    raw_url = match.group(0)
                else:
                    raw_url = values.get("text")
            values["url"] = raw_url
        return values


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
