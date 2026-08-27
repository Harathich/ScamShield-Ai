from fastapi import APIRouter, HTTPException

from app.models.orchestrator_models import FullAnalysisRequest, FullAnalysisResponse, NormalizedMetadata
from app.graph.workflow import scamshield_workflow


router = APIRouter(
    prefix="/analyze-all",
    tags=["Full Analysis Pipeline"]
)


@router.post("/", response_model=FullAnalysisResponse)
def full_analysis(request: FullAnalysisRequest):
    """
    Run the full ScamShield multi-agent analysis pipeline with input preprocessing.

    Accepts any format or key name (e.g. `text`, `message`, `content`, `url`, `body`, raw string).
    Cleans noise/obfuscation, extracts URLs/emails/phones, executes all 5 agents,
    evaluates overall risk through Risk Manager, and generates a user-friendly report.
    """
    try:
        initial_state = {
            "input_text": request.text or "",
            "input_url": request.url,
            "normalized_content": None,
            "threat_result": None,
            "language_result": None,
            "identity_result": None,
            "domain_result": None,
            "recruitment_result": None,
            "risk_manager_result": None,
            "report": None,
            "overall_risk_score": None,
            "overall_threat_level": None,
            "agent_summary": None,
        }

        result = scamshield_workflow.invoke(initial_state)

        risk_manager_result = result.get("risk_manager_result", {})
        norm = result.get("normalized_content", {})

        normalized_metadata = NormalizedMetadata(
            detected_format=norm.get("detected_format", "plain_text"),
            extracted_urls=norm.get("extracted_urls", []),
            extracted_emails=norm.get("extracted_emails", []),
            extracted_phones=norm.get("extracted_phones", [])
        ) if norm else None

        return FullAnalysisResponse(
            overall_risk_score=result.get("overall_risk_score", 0),
            overall_threat_level=result.get("overall_threat_level", "LOW"),
            contributing_factors=risk_manager_result.get("contributing_factors", []),
            confidence=risk_manager_result.get("confidence", 0),
            normalized_metadata=normalized_metadata,
            agent_summary=result.get("agent_summary", {}),
            report=result.get("report"),
            threat_result=result.get("threat_result"),
            language_result=result.get("language_result"),
            identity_result=result.get("identity_result"),
            domain_result=result.get("domain_result"),
            recruitment_result=result.get("recruitment_result"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis pipeline error: {str(e)}"
        )
