from pydantic import BaseModel
from typing import Optional

class OCRResponse(BaseModel):
    success: bool
    extracted_text: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = None
    error: Optional[str] = None
