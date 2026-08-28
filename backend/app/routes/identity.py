from fastapi import APIRouter, HTTPException

from app.agents.identity.agent import IdentityAgent
from app.models.analyze_request import AnalyzeRequest
from app.models.identity_response import IdentityResponse

router = APIRouter(
    prefix="/identity",
    tags=["Identity Verification"]
)

identity_agent = IdentityAgent()


@router.post("/", response_model=IdentityResponse)
def analyze(request: AnalyzeRequest):
    try:
        result = identity_agent.analyze(request.text)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
