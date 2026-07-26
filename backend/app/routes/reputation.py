from fastapi import APIRouter, HTTPException

from app.models.reputation_request import ReputationRequest
from app.models.reputation_response import ReputationResponse
from app.agents.reputation.agent import ReputationAgent


router = APIRouter(
    prefix="/reputation",
    tags=["Reputation Analysis"],
)

reputation_agent = ReputationAgent()


@router.post("/", response_model=ReputationResponse)
def analyze(request: ReputationRequest):

    try:

        result = reputation_agent.analyze(
            str(request.url)
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )