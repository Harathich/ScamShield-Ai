from fastapi import APIRouter, HTTPException

from app.agents.recruiter.agent import RecruiterAgent
from app.models.analyze_request import AnalyzeRequest
from app.models.recruiter_response import RecruiterResponse

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter Scam Detection"]
)

recruiter_agent = RecruiterAgent()


@router.post("/", response_model=RecruiterResponse)
def analyze(request: AnalyzeRequest):
    try:
        result = recruiter_agent.analyze(request.text)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
