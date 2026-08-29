from fastapi import APIRouter, HTTPException

from app.agents.language.agent import LanguageAgent
from app.models.analyze_request import AnalyzeRequest
from app.models.language_response import LanguageResponse

router = APIRouter(
    prefix="/language",
    tags=["Language Analysis"]
)

language_agent = LanguageAgent()


@router.post("/", response_model=LanguageResponse)
@router.post("/analyze", response_model=LanguageResponse)
def analyze(request: AnalyzeRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=422, detail="Provide non-empty text to analyze.")
    try:
        return language_agent.analyze(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))