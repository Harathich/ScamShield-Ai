from fastapi import APIRouter, HTTPException

from app.models.analyze_request import AnalyzeRequest
from app.agents.threat.agent import ThreatAgent
from app.models.threat_response import ThreatResponse

router = APIRouter(
    prefix="/analyze",
    tags=["Threat Analysis"]
)

threat_agent = ThreatAgent()


@router.post("/", response_model=ThreatResponse)
@router.post("/analyze", response_model=ThreatResponse)
def analyze(request: AnalyzeRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=422, detail="Provide non-empty text to analyze.")
    try:
        result = threat_agent.analyze(request.text)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )