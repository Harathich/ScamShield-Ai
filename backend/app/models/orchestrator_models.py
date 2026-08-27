from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, model_validator


class FullAnalysisRequest(BaseModel):
    """
    Highly flexible request model. Accepts any common field name for input text.
    Examples:
      - {"text": "..."}
      - {"message": "..."}
      - {"content": "..."}
      - {"body": "..."}
      - {"url": "..."}
    """
    text: Optional[str] = None
    message: Optional[str] = None
    content: Optional[str] = None
    body: Optional[str] = None
    raw_input: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_any_text(cls, values: Any) -> Any:
        if isinstance(values, str):
            return {"text": values}
        if isinstance(values, dict):
            # Resolve whichever key the user provided
            text = (
                values.get("text")
                or values.get("message")
                or values.get("content")
                or values.get("body")
                or values.get("raw_input")
                or values.get("input")
                or values.get("prompt")
                or ""
            )
            values["text"] = str(text)
        return values


class AgentSummary(BaseModel):
    """Summary of a single agent's result within the orchestrated response."""
    risk_score: Optional[int] = None
    threat_level: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None


class NormalizedMetadata(BaseModel):
    """Metadata extracted by the Content Preprocessor."""
    detected_format: str
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_emails: List[str] = Field(default_factory=list)
    extracted_phones: List[str] = Field(default_factory=list)


class FullAnalysisResponse(BaseModel):
    """Response model for the full multi-agent analysis pipeline."""
    overall_risk_score: int = Field(ge=0, le=100)
    overall_threat_level: str
    contributing_factors: List[str] = Field(default_factory=list)
    confidence: int = Field(ge=0, le=100, default=0)
    normalized_metadata: Optional[NormalizedMetadata] = None
    agent_summary: Dict[str, AgentSummary]
    report: Optional[dict] = None
    threat_result: Optional[dict] = None
    language_result: Optional[dict] = None
    identity_result: Optional[dict] = None
    domain_result: Optional[dict] = None
    recruitment_result: Optional[dict] = None
