from fastapi import APIRouter, HTTPException

from app.models.orchestrator_models import FullAnalysisRequest, FullAnalysisResponse
from app.graph.workflow import scamshield_workflow


router = APIRouter(
    prefix="/analyze-all",
    tags=["Full Analysis Pipeline"]
)


@router.post("/", response_model=FullAnalysisResponse)
def full_analysis(request: FullAnalysisRequest):
    """
    Run the full ScamShield multi-agent analysis pipeline.

    Executes all agents (Threat, Language, Identity, Domain) and returns
    combined results with an overall risk assessment.

    - `text` (required): The suspicious content to analyze.
    - `url` (optional): A specific URL to analyze with the Domain Agent.
      If omitted, the system will attempt to extract a URL from the text.
    """
    try:
        initial_state = {
            "input_text": request.text,
            "input_url": request.url,
            "threat_result": None,
            "language_result": None,
            "identity_result": None,
            "domain_result": None,
            "overall_risk_score": None,
            "overall_threat_level": None,
            "agent_summary": None,
        }

        result = scamshield_workflow.invoke(initial_state)

        return FullAnalysisResponse(
            overall_risk_score=result["overall_risk_score"],
            overall_threat_level=result["overall_threat_level"],
            agent_summary=result["agent_summary"],
            threat_result=result.get("threat_result"),
            language_result=result.get("language_result"),
            identity_result=result.get("identity_result"),
            domain_result=result.get("domain_result"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {str(e)}"
        )
