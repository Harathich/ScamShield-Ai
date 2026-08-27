import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, model_validator


class FullAnalysisRequest(BaseModel):
    """
    Universal flexible request model.
    Accepts ANY payload format:
      - Plain text string
      - Standard keys: {"text": "..."}
      - OCR output JSON: {"extracted_text": "...", "confidence": ...}
      - Alternative keys: {"message": "...", "content": "...", "body": "...", "ocr_text": "..."}
      - Arbitrary dict: automatically extracts the longest text string
    """
    text: Optional[str] = None
    url: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def extract_any_text(cls, values: Any) -> Any:
        if isinstance(values, str):
            # If input is a raw JSON string like '{"extracted_text": "..."}'
            try:
                parsed = json.loads(values)
                if isinstance(parsed, dict):
                    values = parsed
                else:
                    return {"text": values}
            except Exception:
                return {"text": values}

        if isinstance(values, dict):
            # 1. Check direct common text fields including OCR outputs
            text = (
                values.get("text")
                or values.get("extracted_text")
                or values.get("ocr_text")
                or values.get("message")
                or values.get("content")
                or values.get("body")
                or values.get("raw_input")
                or values.get("raw_text")
                or values.get("clean_text")
                or values.get("input")
                or values.get("data")
                or values.get("prompt")
                or values.get("description")
            )

            # 2. If not found in common keys, search all string values and pick the longest
            if not text:
                string_vals = [
                    v for k, v in values.items() 
                    if isinstance(v, str) and k.lower() not in ("url", "error", "language", "status", "type")
                ]
                if string_vals:
                    text = max(string_vals, key=len)

            url = values.get("url") or values.get("link") or values.get("website")

            return {
                "text": str(text).strip() if text else "",
                "url": str(url).strip() if url else None
            }

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
