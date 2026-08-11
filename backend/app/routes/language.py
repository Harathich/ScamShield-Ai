from fastapi import APIRouter

from app.agents.language.agent import LanguageAgent
from app.models.analyze_request import AnalyzeRequest
from app.models.language_response import LanguageResponse

router = APIRouter(
    prefix="/language",
    tags=["Language Analysis"]
)

language_agent = LanguageAgent()


@router.post("/analyze", response_model=LanguageResponse)
def analyze(request: AnalyzeRequest):

    return language_agent.analyze(request.text)