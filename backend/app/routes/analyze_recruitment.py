from fastapi import APIRouter, HTTPException

from app.agents.recruitment.agent import RecruitmentAgent
from app.models.recruitment_models import RecruitmentRequest, RecruitmentResponse

router = APIRouter(
    prefix="/recruitment",
    tags=["Recruitment Analysis"]
)

recruitment_agent = RecruitmentAgent()


@router.post("/", response_model=RecruitmentResponse)
@router.post("/analyze", response_model=RecruitmentResponse)
def analyze(request: RecruitmentRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=422, detail="Provide non-empty recruitment text to analyze.")
    try:
        result = recruitment_agent.analyze(request.text)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
